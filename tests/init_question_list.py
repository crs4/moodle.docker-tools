import argparse
import csv
import os
import sys

import MySQLdb

import load.locust_scripts.settings as setting


def main(filename=setting.QUESTION_FILENAME):
    # user_list = users.generate_users(num_of_users, user_prefix, user_cohort)
    # print "Generated %d users: [ %s ]" % (len(user_list), ", ".join(map((lambda u: u['username']), user_list)))
    # users.write_users(user_list, filename)

    questions = []
    host = os.environ["MYSQL_HOST"]
    user = os.environ["MYSQL_USER"]
    passwd = os.environ["MYSQL_PASSWORD"]
    db = os.environ["MYSQL_DATABASE"]

    cnx = MySQLdb.connect(host, user, passwd, db)
    try:
        cursor = cnx.cursor()

        query = ("SELECT q.id, q.name, q.qtype FROM moodle.mdl_question as q WHERE q.qtype like 'omero%'")

        cursor.execute(query)

        for (qid, qname, qtype) in cursor:
            questions.append({
                "id": qid,
                "name": qname,
                "type": qtype
            })
        cursor.close()
        cnx.close()

        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['id', 'name', 'type'])
            writer.writeheader()
            for question in questions:
                writer.writerow(question)
        return questions

    except MySQLdb.Error, e:
        try:
            print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
        except IndexError:
            print "MySQL Error: %s" % str(e)
        return False
    cnx.close()
    return True


if __name__ == "__main__":
    raw_args = sys.argv[1:]
    parser = argparse.ArgumentParser(description='Initialize the list of MOODLE OmeroQuestions.')
    parser.add_argument('-f', '--filename', default=setting.QUESTION_FILENAME,
                        help='filename containing the list of OmeroQuestions (default: "' + setting.QUESTION_FILENAME + '")')
    args = parser.parse_args(raw_args)

    if hasattr(args, 'help') and args.help:
        parser.print_help()
    else:
        main(filename=args.filename)
