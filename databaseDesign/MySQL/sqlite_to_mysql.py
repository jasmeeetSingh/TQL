import re
import fileinput

def this_line_is_useless(line):
    useless_es = [
        'BEGIN TRANSACTION',
        'COMMIT',
        'sqlite_sequence',
        'CREATE UNIQUE INDEX',        
        'PRAGMA foreign_keys=OFF',
        'PRAGMA foreign_keys=ON',
        'PRAGMA foreign_keys = OFF',
        'PRAGMA foreign_keys = ON'

        ]
    for useless in useless_es:
        if re.search(useless, line):
            return True

def has_primary_key(line):
    return bool(re.search(r'PRIMARY KEY', line))

def sqlite_to_mysql(filename):
    searching_for_end = False
    lines = ''
    for line in fileinput.input(filename):
        if this_line_is_useless(line): continue

        # this line was necessary because ''); was getting
        # converted (inappropriately) to \');
        if re.match(r".*, ''\);", line):
            line = re.sub(r"''\);", r'``);', line)

        if re.match(r'^CREATE TABLE.*', line):
            searching_for_end = True

        m = re.search('CREATE TABLE "?([A-Za-z_]*)"?(.*)', line)
        if m:
            name, sub = m.groups()
            line = "DROP TABLE IF EXISTS %(name)s;\nCREATE TABLE IF NOT EXISTS `%(name)s`%(sub)s\n"
            line = line % dict(name=name, sub=sub)
            line = line.replace('AUTOINCREMENT','AUTO_INCREMENT')
            line = line.replace('UNIQUE','')
            line = line.replace('"','')
        else:
            m = re.search('INSERT INTO "([A-Za-z_]*)"(.*)', line)
            if m:
                line = 'INSERT INTO %s%s\n' % m.groups()
                line = line.replace('"', r'\"')
                line = line.replace('"', "'")
                line = re.sub(r"(?<!')'t'(?=.)", r"1", line)
                line = re.sub(r"(?<!')'f'(?=.)", r"0", line)

        # Add auto_increment if it's not there since sqlite auto_increments ALL
        # primary keys
        if searching_for_end:
            if re.search(r"integer(?:\s+\w+)*\s*PRIMARY KEY(?:\s+\w+)*\s*,", line):
                line = line.replace("PRIMARY KEY", "PRIMARY KEY AUTO_INCREMENT")
            # replace " and ' with ` because mysql doesn't like quotes in CREATE commands

        # And now we convert it back (see above)
        if re.match(r".*, ``\);", line):
            line = re.sub(r'``\);', r"'');", line)

        if searching_for_end and re.match(r'.*\);', line):
            searching_for_end = False

        if re.match(r"CREATE INDEX", line):
            line = re.sub('"', '`', line)

        lines = lines + line

    if lines[-1] == '\n':
        sql_statments = lines[:-2].replace('\n', ' ').replace('"','').replace('text', 'varchar(255)').split(';')
    else:
        sql_statments = lines
        
    return sql_statments