from fastapi import FastAPI
import pandas as pd 
import numpy as np

app = FastAPI(title='Proyecto individual 1: Recomendacion de peliculas',
            description='API de datos y recomendaciones de películas')

#http://127.0.0.1:8000


@app.on_event("startup")
async def load_data():
    global credits_final, movies_final
    # Carga los datos
    credits_final = pd.read_csv('credits_final.csv')
    movies_final = pd.read_csv('movies_final.csv')

@app.get('/')
async def read_root():
    return {'Mi primera API. Dirígite a /docs'}

@app.get('/about/')
async def about():
    return {'Proyecto individual 1: Recomendacion de peliculas'}

@app.get('/cantidad_filmaciones_mes/{mes}')
def cantidad_filmaciones_mes(mes:str):
  mes = mes.lower()
  meses = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12}
  mes_nro = meses.get(mes)
  estrenos = movies_final[movies_final['release_date'].dt.month == mes_nro]
  cantidad = len(estrenos['id'].unique())
  return {'mes':mes.capitalize(), 'cantidad':cantidad}

@app.get('/cantidad_filmaciones_dia{dia}')
def cantidad_filmaciones_dia(dia:str):
  dia = dia.lower()
  dias = {'lunes': 'Monday', 'martes': 'Tuesday', 'miercoles': 'Wednesday', 'jueves': 'Thursday', 'viernes': 'Friday', 'sabado': 'Saturday', 'domingo': 'Sunday'}
  dia_en = dias.get(dia)
  estrenos = movies_final[movies_final['release_date'].dt.day_name() == dia_en]
  cantidad = len(estrenos['id'].unique())
  return {'dia':dia.capitalize(), 'cantidad':cantidad}

@app.get('/score_titulo/{titulo}')
def score_titulo(titulo:str):
  title = titulo.replace(" ", "").lower()
  movie_c = movies_final[movies_final['title'].str.replace(" ", "").str.lower().str.contains(title)].drop_duplicates(subset='id')
  if movie_c.empty:
        return f'No se encontró la película {titulo} en la base de datos.'
  movie = movie_c['title'].iloc[0]
  year = movie_c['release_year'].iloc[0]
  popularity = movie_c['popularity'].iloc[0]
  return {'titulo':movie, 'anio':year, 'popularidad':popularity}

@app.get('/votos_titulo/{titulo}')
def votos_titulo(titulo:str):
  title = titulo.replace(" ", "").lower()
  movie_c = movies_final[movies_final['title'].str.replace(" ", "").str.lower().str.contains(title)].drop_duplicates(subset='id')
  if movie_c.empty:
        return f'No se encontró la película {titulo} en la base de datos.'
  if (movie_c['vote_count'].iloc[0]<2000):
    return f'La película {titulo} debe tener al menos 2000 valoraciones para ser medida'
  #vote_average	vote_count
  movie = movie_c['title'].iloc[0]
  year = movie_c['release_year'].iloc[0]
  vote_count = movie_c['vote_count'].iloc[0]
  vote_average = movie_c['vote_average'].iloc[0]
  return  {'titulo':movie, 'anio':year, 'voto_total':vote_count, 'voto_promedio':vote_average}

@app.get('/get_actor/{nombre_actor}')
def get_actor(nombre_actor:str):
  actor = nombre_actor.replace(" ", "").lower()
  mask = credits_final['cast_name'].str.replace(" ", "").str.lower().str.contains(actor)
  # Filtrar el DataFrame para mostrar solo las filas donde se encontró el nombre
  filtered = credits_final[mask]
  filtered_movies = movies_final[(movies_final['id'].astype(int)).isin(filtered['id'].astype(int))].drop_duplicates(subset='id')
  cantidad = len(filtered)
  return_movies = round(filtered_movies['return'].sum(), 3)
  if cantidad > 0:
      average = round(return_movies / cantidad, 3)
  else:
      average = 0
  return {'actor':nombre_actor.title(), 'cantidad_filmaciones':cantidad, 'retorno_total':return_movies, 'retorno_promedio':average}

@app.get('/get_director/{nombre_director}')
def get_director(nombre_director:str):
  director = nombre_director.replace(" ", "").lower()
  mask = credits_final['director'].str.replace(" ", "").str.lower().str.contains(director)
  # Filtrar el DataFrame para mostrar solo las filas donde se encontró el nombre
  filtered = credits_final[mask]
  filtered_movies = movies_final[(movies_final['id'].astype(int)).isin(filtered['id'].astype(int))].drop_duplicates(subset='id')
  return_movies = round(filtered_movies['return'].sum(), 3)
  movies = ', '.join(filtered_movies['title'].astype(str))
  year = ', '.join(filtered_movies['release_year'].astype(str))
  return_movie = ', '.join(filtered_movies['return'].astype(str).apply(lambda x: str(round(float(x), 3))))
  budget = ', '.join(filtered_movies['budget'].astype(str).apply(lambda x: str(round(float(x), 3))))
  revenue = ', '.join(filtered_movies['revenue'].astype(str).apply(lambda x: str(round(float(x), 3))))

  return  {'director':nombre_director.title(), 'retorno_total_director':return_movies,
    'peliculas':movies, 'anio':year, 'retorno_pelicula':return_movie,
    'budget_pelicula':budget, 'revenue_pelicula':revenue}