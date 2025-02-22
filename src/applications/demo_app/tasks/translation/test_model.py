import torch
import torch.nn.functional as F
import importlib
from src.utilities.load_data import *
from src.modules.models.base_component import gen_pad_only_mask, gen_seq_only_mask, gen_full_false_mask
from src.modules.tester.tester_framework import Tester
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from build_dataset import *
from build_model import TestingModel


def test_model(config):
    # step 1: load model and config states
    load_model_states_into_config(config)
    # step 2: get the tester
    tester = Tester(config)
    # step 3: get the data iterator and field
    test_iter = build_test_dataset_pipeline(config)
    # step 4: get the model and update config
    model = load_model_and_vocab(config)
    # step 5: start test
    used_model = config['model_config']['model_name']
    src_transforming_key = eval(config['test_text_transforming_adaptor'][used_model]['source_seqs'])[1]
    tgt_transforming_key = eval(config['test_text_transforming_adaptor'][used_model]['target_seqs'])[1]
    src_vocab = config['vocab_config'][src_transforming_key]
    tgt_vocab = config['vocab_config'][tgt_transforming_key]
    tgt_pad_idx = config['symbol_config'][tgt_transforming_key]['pad_idx']
    tester.test(model=model, test_iter=test_iter,
                  compute_predict_evaluation_func=compute_predict_evaluation,
                  compute_predict_evaluation_outer_params={
                      'src_vocab': src_vocab, 'tgt_vocab': tgt_vocab, 'pad_idx': tgt_pad_idx})


# this function needs to be defined from the view of concrete task
def compute_predict_evaluation(model, data_example, max_len, device, do_log, log_string_list, src_vocab, tgt_vocab, pad_idx):
    # model, data_example, device, do_log, log_string_list are from inner tester framework
    # output: predict: N,L,D,  target: N,L
    if data_example[0].size(1) > max_len:
        source = data_example[0][:, :max_len].to(device)
    else:
        source = data_example[0].to(device)
    if data_example[1].size(1) > max_len:
        target = data_example[1][:, :max_len].to(device)
    else:
        target = data_example[1].to(device)
    target_real = target[:, 1:-1]     # remove sos_token and end_sos_token, there should be no pad_token
    sos_idx = target[0, 0].item()
    eos_idx = target[0, -1].item()
    predict = greedy_decode(model.model, source, device, max_len, sos_idx, eos_idx, pad_idx)
    evaluation = model.evaluator(predict, target_real)
    if do_log:
        log_string_list.append(
            "Source string:  " + ' '.join(src_vocab.get_itos()[index] for index in source[0, 1:-1]))    #可能有的词会被替换成<unk>输出，因为在soti的时候在字典里查不到。
        log_string_list.append("Source code:    " + ' '.join(str(index.item()) for index in source[0, 1:-1]))
        log_string_list.append(
            "Target string:  " + ' '.join(tgt_vocab.get_itos()[index] for index in target[0, 1:-1]))
        log_string_list.append("Target code:    " + ' '.join(str(index.item()) for index in target[0, 1:-1]))
        log_string_list.append("Predict string: " + ' '.join(tgt_vocab.get_itos()[index] for index in predict[0, 1:]))
        log_string_list.append("Predict code:   " + ' '.join(str(index.item()) for index in predict[0, 1:]) + '\n')
    return predict, target_real, evaluation


def greedy_decode(model, source, device, max_len, sos_idx, eos_idx, pad_idx=None):
    src_key_padding_mask = memory_key_padding_mask = gen_pad_only_mask(source, pad_idx)   #N,L
    enc_out = model.encoder(source, src_key_padding_mask=src_key_padding_mask)
    target_input = torch.ones(1, 1).fill_(sos_idx).type(torch.long).to(device)
    for i in range(max_len - 1):
        tgt_key_padding_mask = gen_pad_only_mask(target_input, pad_idx)  # N,L
        tgt_mask = gen_seq_only_mask(target_input, target_input)  # L,L
        dec_out = model.decoder(target_input, enc_out, tgt_mask=tgt_mask, tgt_key_padding_mask=tgt_key_padding_mask, memory_key_padding_mask=memory_key_padding_mask)
        last_logit = model.predictor(dec_out[:, -1:])
        last_word = F.softmax(last_logit, dim=-1).argmax(dim=-1)     # last_word size: (1,1)
        if last_word.item() == eos_idx:
            break
        target_input = torch.cat([target_input, last_word], dim=-1)
    predict = target_input
    return predict


def load_model_and_vocab(config):
    model_state_dict = config['model_state_dict']
    model = TestingModel(config)
    model.model.load_state_dict(model_state_dict)
    return model


def load_model_states_into_config(config):
    model_save_root = config['check_point_root']
    saved_model_file = config['net_structure']['saved_model_file']
    model_file_path = model_save_root + os.path.sep + saved_model_file
    model_states = torch.load(model_file_path)
    config.update(model_states)
