## 运行 talk2navi_1.0
`python main.py plugins/shortest_path_calculation.py`  

## 扩充 talk2navi_1.0
1.在plugins文件夹可以自定义function供大模型calling
2.在[微调平台](https://platform.openai.com/finetune/ftjob-eJuMkF472I8WfDtmLmSXmPdr?filter=all)训练后的大模型，可在src/session/session.py中更改13行和15行的模型名称进行调用
