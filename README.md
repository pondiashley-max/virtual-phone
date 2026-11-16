virtual phone whatsapp messenger system

two independent virtual phones (alpha phone and beta phone) built with django, supporting text message sharing, file sharing, image/photo sharing, audio notes, and video clips sharing over the internet.

features:
- two independent web apps in separate subfolders (phone_alpha and phone_beta)
- whatsapp-style chat messenger interface with chat bubbles
- text message sharing
- file, image, audio, and video sharing with size boundaries and view/download links
- built with django backend and sqlite database

how to run:
cd "virtual phone"
python server.py runserver 8001

access:
alpha phone: http://127.0.0.1:8001/alpha/
beta phone: http://127.0.0.1:8001/beta/
