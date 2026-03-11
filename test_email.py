import smtplib

try:
    with smtplib.SMTP_SSL('smtp.timeweb.ru', 465) as server:
        server.login('cocktails@softspacecompany.com', 'sV397bA7l')
        print("Успешная аутентификация!")
except Exception as e:
    print(f"Ошибка: {e}")