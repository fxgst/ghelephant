class Inserter:
    @staticmethod
    def insert_actor(cursor, actor):
        query = 'INSERT INTO actor (id, login) VALUES (%s, %s) ON CONFLICT DO NOTHING'
        data = (actor['id'], actor['login'])
        cursor.execute(query, data)

    @staticmethod
    def insert_repo(cursor, repo):
        owner, name = repo['name'].split('/')

        data = (repo['id'], owner, name)
        query = 'INSERT INTO repo (id, owner, name) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING'
        cursor.execute(query, data)
