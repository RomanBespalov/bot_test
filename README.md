# bot_test  

ТЗ:  
Интерфейс для рассылки сообщений и аналитики рассылок.  

Сделать Django интерфейс для рассылки сообщений используя следующие требования  

Основные модели:  
- Шаблон рассылок  
- Рассылка  
- Юзер  
- Кнопка  

Требования:  
- Возможность делать рассылку из шаблона (редактируя ее) или создать вручную  
- Отправить тестовое сообщение (по кнопке вписываем username и отправляется созданное сообщение без закрытия интерфейса редактирования)  
- Выбрать юзера и посмотреть какие рассылки делали  
- Фильтр по результатам рассылки (какие юзеры купили, какие блокнули, какие нажали кнопку)  

Фильтры для юзеров:  
- Фильтр по шаблону  
- Фильтр по рассылке  
- Фильтр по нажатым кнопкам  
- Фильтр по заблокированным юзерам  