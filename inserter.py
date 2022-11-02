class Inserter:
    @staticmethod
    def insert_actor(cursor, actor):
        query = 'INSERT INTO actor (id, login) VALUES (%s, %s) ON CONFLICT DO NOTHING'
        data = (actor['id'], actor['login'])
        cursor.execute(query, data)
