# THE1000X-BOT-PRO 📈🤖

بوت تداول عقود آجلة باستراتيجية تعزيز تدريجية وواجهة Streamlit لمراقبة السوق.

## المكونات

- `bot.py`: البوت الأساسي
- `streamlit_app.py`: واجهة Streamlit
- `config.py`: تخزين المفاتيح (API و Telegram)
- `requirements.txt`: قائمة المكتبات المطلوبة

## طريقة التشغيل

1. ثبّت المتطلبات:
```
pip install -r requirements.txt
```

2. شغّل البوت:
```
python bot.py
```

3. شغّل الواجهة:
```
streamlit run streamlit_app.py
```

## ملاحظات

- تأكد من وضع مفاتيحك الخاصة في `config.py`
- يُفضل تشغيل البوت على VPS
- Streamlit Cloud لا يدعم أوامر التداول المباشر (فقط العرض)