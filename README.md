# model-training-framework

## 概述

本开源框架的目标是把模型训练过程中的通用流程和组件整理成可以复用的框架模板，使得开发者可以聚焦算法模型本身，同时提高模型配置和部署的灵活性。

框架代码写得还有点糙，有许多需要优化的地方，比如对函数入参的合法性验证、性能优化等。注释写得也不全。

欢迎有缘者多多指正！

## 指导思想：

接到一个AI项目或产品需求后，如何着手进行开发？可以从如下两个角度考虑：

#### 1. 从框架角度：

（1）首先根据需求把项目分解成应用任务，比如意图识别。<br>
（2）然后把应用任务分解成基础任务，比如文本分类。<br>
（3）设计或选择基础任务的构成组件：分词器、模型结构、目标函数、优化器、学习率调节器、性能评价指标。<br>

#### 2. 从流程角度：

模型训练的完整流程包括：数据预处理、模型训练、模型验证、模型保存、模型加载、模型测试、模型应用等。<br>

#### 3. 从工程部署角度：

项目会包含许多超参数等配置参数，要实现代码和配置参数相分离。<br>

## 框架特点：

（1）基于Pytorch框架。<br>
（2）实现数据预处理（TorchText框架）、模型训练、模型验证和模型测试的流程化配置管理。<br>
（3）实现分词器、模型结构、目标函数、优化器、评价指标、训练框架、测试框架的模块化配置管理。<br>
（4）实现配置和代码相分离的超参数配置管理。<br>
（5）包含了一些实用的技巧，比如数据预处理的多进程并发、断点续训（check_point）、梯度裁剪等。<br>

## 框架代码目录结构：
> file_config.yaml ----------------------------*主框架文件及目录配置文件*<br>
> run.py --------------------------------------*项目程序执行入口文件*<br>
> src -----------------------------------------*源代码文件目录*<br>
> 
>> arguments ----------------------------------*存放配置参数文件的目录*<br>
>> 
>>> datasets ----------------------------------*存放数据集相关参数配置文件的目录*<br>
>>> models ------------------------------------*存放模型相关参数配置文件的目录*<br>
>>> tasks -------------------------------------*存放应用任务相关参数配置文件的目录*<br>
>>
>> models -------------------------------------*存放模型代码的目录*<br>
>> 
>>> criteria ----------------------------------*目标函数*<br>
>>> evaluators --------------------------------*性能评价指标*<br>
>>> models ------------------------------------*模型结构*<br>
>>> optimizers --------------------------------*优化器*<br>
>>> tester ------------------------------------*测试框架*<br>
>>> tokenizers --------------------------------*分词器*<br>
>>> trainer -----------------------------------*训练框架*<br>
>>> vectors -----------------------------------*词向量*<br>
>>
>> tasks --------------------------------------*存放应用任务的目录*<br>
>> 
>>> answer_grade ------------------------------*示例任务：问答打分*<br>
>>> 
>>>> preprocess.py ----------------------------*示例任务代码：划分数据集、数据清洗等模型训练前置任务*<br>
>>>> build_dataset.py -------------------------*示例任务代码：中文分词、创建数据生成器等*<br>
>>>> build_model.py ---------------------------*示例任务代码：创建模型对象*<br>
>>>> train_model.py ---------------------------*示例任务代码：训练模型*<br>
>>>> test_model.py ----------------------------*示例任务代码：测试模型*<br>
>>>> apply.py ---------------------------------*示例任务代码：应用模型*<br>
>>> 
>>> data_crawling -----------------------------*示例任务：数据爬取*<br>
>>> neo4j -------------------------------------*示例任务：知识图谱搜索*<br>
>>> ner ---------------------------------------*示例任务：命名实体识别*<br>
>>> translation -------------------------------*示例任务：机器翻译*<br>
>>
>> tests --------------------------------------*存放接口测试代码文件的目录*<br>
>> utilities ----------------------------------*存放底层工具代码文件的目录*<br>
>
> dataset -------------------------------------*存放数据集资源的目录*<br>
>> bert_model ---------------------------------*bert模型*<br>
>> word_vector --------------------------------*静态词向量*<br>
>> for xxx ------------------------------------*示例：针对特定任务的数据集*<br>
>
>data -----------------------------------------*存放系统产生的数据文件的目录*<br>
>
>> log ----------------------------------------*日志*<br>
>> model --------------------------------------*保存的模型*<br>
>> 
>>> answer_grade ------------------------------*示例任务：问答打分*<br>
>>> ner ---------------------------------------*示例任务：命名实体识别*<br>
>>> translation -------------------------------*示例任务：机器翻译*<br>

## 基本使用方法：

- 收集整理数据集、词向量等数据文件存入dataset目录下相应位置
- 在src/models目录下相应位置编写模型代码
- 在src/tasks目录下相应位置编写模型定义、数据预处理、模型训练和测试代码
- 在src/arguments目录下相应位置编写配置参数
- 在src/tests目录下写必要的接口测试代码
- 训练和测试模型
