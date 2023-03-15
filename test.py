import requests

url = "https://fantasy.espn.com/tournament-challenge-bracket/2023/en/createOrUpdateEntry?b=02|03|05|07|09|11|13|15|17|19|22|23|25|28|29|31|33|35|37|40|41|43|45|47|50|52|54|55|58|59|62|63|02|05|11|15|17|23|25|31|33|40|43|47|52|55|59|63|02|11|23|31|33|43|52|63|11|31|33|63|31|33&r=entry&t1-72&t2=65"

payload={}
headers = {
  'cookie': 'espn_s2=AEBNLoWaeZzF3TPfzrrhWSfX8WvhrPzlZwGKbh/qiyb0y2euI8wpkeFjf/2CTKxDPPoERSaiD0lXkqSehfHm3Z7bFTcbciRk7XQKrWbb9uYcAWqHMbS76dZYCydz+q3L3QYF5PYjc9uJeqoVwcRQneRqjem5tfcUu5clrn3/ga7NQ8BQDajooyt/LBxiblGQvsFnEcoz97KiSbNZoadhfz9bj3f+cu0qmqSFeSv9O2WqaroA1xQfoNjONOaZQ119fLa2711ffg1PQl9XpJK5tKBSNw8XFQJzzaL7Lr9Hc1DDAg=='
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
