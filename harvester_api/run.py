from app import app


if __name__ == '__main__':
    env_name = 'development'
    app = app(env_name)
    app.run()
