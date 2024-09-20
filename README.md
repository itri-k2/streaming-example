### 介紹
為了讓demo時，前端能夠看起來是有變化的，而不是最後才將所有結果一次輸出，因此api需要改為streaming的方式。
我在main.py寫了一個streaming api的範例，你們可以參考一下。


### step1 安裝套件

```=bash
pip install -r requirements.txt
```

### step2 啟動server

```=bash
python main.py
```

### step3 測試API的功能

```=bash
python test.py
```

成功的話應該會看到兩種結果

1. is_intent為true
```
{'is_intent': False, 'details': {'polygon': '(138.5607, 15.7915), (99.8672, 89.0884), (72.0231, 16.6307), (138.5607, 76.9646)', 'RAT': 'NR', 'DL ARFCN': '470503', 'Weak RSRP ratio': '69', 'Weak RSRP threshold': '-17', 'Low SINR ratio': '72', 'Low SINR threshold': '-91', 'highDlPrbLoadRatioTarget': None, 'MbpsaveDLRANUEThptTarget': None, 'highDlPrbLoadRatioTarget.HighDlPrbLoad': None}}
```

2. is_intent為false
```
{'is_intent': False, 'content': ''}
{'is_intent': False, 'content': ' A B C  A B C  A B C  A B C  A B C '}
{'is_intent': False, 'content': ' A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C '}
{'is_intent': False, 'content': ' A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C '}
{'is_intent': False, 'content': ' A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C '}
{'is_intent': False, 'content': ' A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C '}
{'is_intent': False, 'content': ' A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C '}
{'is_intent': False, 'content': ' A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C '}
{'is_intent': False, 'content': ' A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C '}
{'is_intent': False, 'content': ' A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C  A B C '}
```

### 補充
將程式碼上傳到github時我希望能包含requirements.txt
把使用到的package及對應的版本同步給我們
可以在你使用的python的虛擬環境中(pipenv或venv)用下面的指令
```bash=
pip freeze > requirements.txt
```

#### ！！！請不要在python的虛擬環境外使用pip freeze！！！
這會把用不到的套件一起上傳
