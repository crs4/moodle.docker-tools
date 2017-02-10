import sys, argparse
from load.test_scripts import users
from load.test_scripts import settings


def main(num_of_users,
         user_prefix=settings.USER_PREFIX,
         user_cohort=settings.USER_COHORT,
         filename=settings.USERS_FILENAME):
    user_list = users.generate_users(num_of_users, user_prefix, user_cohort, as_dict=True)
    print "Generated %d users: [ %s ]" % (len(user_list), ", ".join(map((lambda u: u["username"]), user_list)))
    users.write_users(user_list, filename)


if __name__ == "__main__":
    raw_args = sys.argv[1:]
    parser = argparse.ArgumentParser(description='Initialize the list of MOODLE user.')
    parser.add_argument('-f', '--filename', default=settings.USERS_FILENAME,
                        help='filename containing the list of users to create (default: "' + settings.USERS_FILENAME + '")')
    parser.add_argument('-p', '--prefix', default=settings.USER_PREFIX,
                        help='user prefix: "' + settings.USER_PREFIX + '")')
    parser.add_argument('-c', '--cohort', default=settings.USER_COHORT,
                        help='user cohort: "' + settings.USER_COHORT + '"')
    parser.add_argument('users', default=1, type=int, help='number of users to create (default: 1)')
    args = parser.parse_args(raw_args)

    if hasattr(args, 'help') and args.help:
        parser.print_help()
    else:
        main(num_of_users=args.users,
             user_prefix=args.prefix, user_cohort=args.cohort,
             filename=args.filename)
