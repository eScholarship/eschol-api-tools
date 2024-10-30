def process_args():
    import argparse
    parser = argparse.ArgumentParser()

    def validate_connection(arg):
        arg = arg.upper()
        if not (arg == 'DEV' or arg == 'QA' or arg == 'PROD'):
            raise ValueError
        return arg

    parser.add_argument("-c", "--connection",
                        dest="connection",
                        type=validate_connection,
                        default='qa',
                        help="Specify 'dev', 'qa', or 'prod' only.")

    parser.add_argument("-i", "--input",
                        dest='input_file',
                        help="Specify an input file.")

    parser.add_argument("--clear-previous",
                        dest="clear_previous",
                        action='store_true',
                        default=False,
                        help="Add this tag to clear the previous labels (etc)")

    return parser.parse_args()


def get_config():
    from dotenv import dotenv_values
    return dotenv_values(".env")


def get_eschol_api_connection(con, config):
    eschol_api = {
        'url':      config['ESCHOL_API_URL_' + con] + "/graphql/",
        'priv_key': config['ESCHOL_API_PRIV_KEY_' + con]}

    if con == 'QA' or con == 'DEV':
        eschol_api['cookie'] = config['ESCHOL_API_COOKIE_' + con]

    return eschol_api
