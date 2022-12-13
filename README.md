# Stinky
 
## Instalation

Кароче щоб запустити проект, файл run.py це точка входу програми, там міняєш API на свого бота, і id на свій телеграм id, не забуваєш встановити всі ліби з requirements.txt і можеш запускати run.py

## Compilation

Щоб скомпілювати юзай pyinstaller
```ruby
pip install pyinstaller
```
Компілюєш файл точки входу програми, pyinstaller сам загрузить всі ліби і інші файли що юзаються в програмі
```ruby
pyinstaller --onefile --noconsole run.py
```
Готова програма скомпілюється в папку dist
+ onefile - скомпілює весь код в один файл exe
+ noconsole - зробить щоб при запуску не запускалась консоль
