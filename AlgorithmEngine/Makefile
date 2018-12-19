root:=$(shell readlink -f .)
py_lib:=$(shell readlink -f ./lib)

all: CTPMarketData MarketData SaveTick RedisLogMain FlaskWeb Init ServerApp Launcher StrategyLauncher CoreEngine package
	
ServerApp:
	pyinstaller -p $(root) TradeEngine/ServerApp.py

sysopr:
	pyinstaller -p $(root) ExternalProgramma/sysopr.py

Launcher:
	pyinstaller -p $(root) -F Launcher.py

StrategyLauncher:
	pyinstaller -p $(root) -F StrategyLauncher.py

CoreEngine:
	pyinstaller -p $(root) TradeEngine/CoreEngine.py

RedisLogMain:
	pyinstaller -p $(root) Common/RedisLogMain.py

CTPMarketData:
	cd MarketDataServer/CTPClient/;make clean;make
	mkdir -p CTPMarketDataPackage
	cp MarketDataServer/CTPClient/run.conf CTPMarketDataPackage
	cp MarketDataServer/CTPClient/*.sh CTPMarketDataPackage
	cp MarketDataServer/CTPClient/build/CTPDataClient CTPMarketDataPackage

SaveTick:
	pyinstaller -p $(root) ExternalProgramma/SaveTickDataToRedis.py

MarketData:
	pyinstaller -p $(root) -p $(root)/MarketDataServer MarketDataServer/MarketDataMain.py

FlaskWeb:
	pyinstaller -p $(root) StartWebServer.spec

Init:
	pyinstaller -p $(root) -F init.py

package:
	mkdir -p TradePlatform
	cp -fr dist/* TradePlatform
	cp -rf CTPMarketDataPackage TradePlatform
	cp -rf lib TradePlatform
	cp -rf CTPTradeClient
	cp -f config.json TradePlatform
	zip -r TradePlatform

clear:
	-rm -rf build dist TradePlatform