from flask import Flask, jsonify, request
import db

app = Flask(__name__)


# --- Utility functions ---

def filter_by_type(pokemons, selected_type):
    if not selected_type:
        return pokemons
    return [
        pokemon for pokemon in pokemons
        if selected_type.lower() in (
            pokemon.get('type_one', '').lower(),
            pokemon.get('type_two', '').lower()
        )
    ]


def filter_by_query(pokemons, query):
    if not query:
        return pokemons
    query_lower = query.lower()
    return [
        pokemon for pokemon in pokemons
        if query_lower in pokemon.get('name', '').lower()
    ]


def sort_pokemons(pokemons, sort_option):
    reverse = sort_option.endswith('desc')
    return sorted(
        pokemons,
        key=lambda pokemon: pokemon.get('_id', 0),
        reverse=reverse
    )


def paginate_pokemons(pokemons, limit, cursor):
    start_index = 0
    if cursor:
        start_index = next(
            (i + 1 for i, pokemon in enumerate(pokemons)
             if str(pokemon.get('_id')) == str(cursor)),
            0
        )

    paginated_pokemons = pokemons[start_index:start_index + limit]
    next_cursor = None
    if start_index + limit < len(pokemons):
        next_cursor = str(paginated_pokemons[-1]['_id'])

    return paginated_pokemons, next_cursor


def extract_types(pokemons):
    pokemon_types = set()
    for pokemon in pokemons:
        if pokemon.get('type_one'):
            pokemon_types.add(pokemon['type_one'])
        if pokemon.get('type_two'):
            pokemon_types.add(pokemon['type_two'])
    return sorted(pokemon_types)


# --- Routes ---

@app.route('/icon/<name>')
def get_icon_url(name: str):
    return f"https://img.pokemondb.net/sprites/silver/normal/{name}.png"


@app.route('/pokemons')
def get_pokemons():
    all_pokemons = db.get()

    # Filters
    selected_type = request.args.get('type')
    query = request.args.get('searchText')
    sort_option = request.args.get('sort', 'number_asc')
    limit = int(request.args.get('limit', 20))
    cursor = request.args.get('cursor')

    filtered_pokemons = filter_by_type(all_pokemons, selected_type)
    filtered_pokemons = filter_by_query(filtered_pokemons, query)
    sorted_pokemons = sort_pokemons(filtered_pokemons, sort_option)
    paginated_pokemons, next_cursor = paginate_pokemons(sorted_pokemons, limit, cursor)

    return jsonify({
        'items': paginated_pokemons,
        'nextCursor': next_cursor
    })


@app.route('/types')
def get_types():
    all_pokemons = db.get()
    types_list = extract_types(all_pokemons)
    return jsonify(types_list)


if __name__ == '__main__':
    app.run(port=8080, debug=True)
