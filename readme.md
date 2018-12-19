- Please install python2.7 frist.

- If running system is not mac or linux, please edit ```./backtest/dataServer/Conf.py```

  ```
  CACHE = True
  DEFAULT = '127.0.0.1'
  DATA_PATH = '/tmp' # Change this to make sure this path is exsit or just chang to '.'.
  DB_PATH = None
  ```

- Install deps

  ```
  pip install -r requirements-maybe.txt
  ```

- Start dataService

  ```
  cd dataServer/
  python net_GTADataBase.py 
  ```

- Start testStrategy.py

  ```
  cd backtest/
  python testStrategy.py
  ```

- The detail of backtest please see tutorial-sample-strategy-en.ipynb.

  > Make sure you have installed ipython notebook.
  >
  > And you can upload this file to ipython notebook.
  >
  >
  >
  > ![image-20181219154728259](https://ws4.sinaimg.cn/large/006tNbRwly1fyc3q1jzcnj31y209mab4.jpg)
