from microservices import app
import config


if __name__ == '__main__':
    app.run(port=config.EXPOSED_PORT,
            debug=config.debug)