# -*- coding: utf-8 -*-
 
##
## INCLUIR LA CABECERA AQUI
## 


@get('/find_users')
def find_users():
    # http://localhost:8080/find_users?name=Luz
    # http://localhost:8080/find_users?name=Luz&surname=Romero
    # http://localhost:8080/find_users?name=Luz&&surname=Romero&birthdate=2006-08-14


@get('/find_email_birthdate')
def email_birthdate():
    # http://localhost:8080/find_email_birthdate?from=1973-01-01&to=1990-12-31


@get('/find_country_likes_limit_sorted')
def find_country_likes_limit_sorted():
    # http://localhost:8080/find_country_likes_limit_sorted?country=Irlanda&likes=movies,animals&limit=4&ord=asc


@get('/find_birth_month')
def find_birth_month():
  # http://localhost:8080/find_birth_month?month=abril


@get('/find_likes_not_ending')
def find_likes_not_ending():
  # http://localhost:8080/find_likes_not_ending?ending=s


@get('/find_leap_year')     
def find_leap_year():
  # http://localhost:8080/find_leap_year?exp=20




###################################
# NO MODIFICAR LA LLAMADA INICIAL #
###################################
if __name__ == "__main__":
    run(host='localhost',port=8080,debug=True)
