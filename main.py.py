from operator import length_hint
import psycopg2
import os
import errno
import time
inicio = time.time()


try:
    os.mkdir('DAO')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

try:
    os.mkdir('Modelo')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

db_name = ''
db_host = ''
db_port = 5411
db_user = ''
db_password = ''
java_var = []
prefix = ""


class DataBase:
    def __init__(self) -> None:
        self.connection = psycopg2.connect(
            host=db_host,
            password='',
            port=db_port,
            database=db_name
        )

        self.cursor = self.connection.cursor()
        print("Conexion establecida")

    def getTables(self, condicion):
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ".format(
            condicion)
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()

        except Exception as e:
            print(e)

    def getColumn(self, table):
        sql = " SELECT * FROM	information_schema.columns WHERE table_schema = 'public'	AND table_name = '{}' ".format(
            table)
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()

        except Exception as e:
            print(e)


database = DataBase()
db_tables = database.getTables("")


for t in db_tables:
    print('------')
    print(t[0])
    db_colum = database.getColumn(t[0])
    java_object = t[0].capitalize()
    java_var = []
    for c in db_colum:
        print('\t'+c[3])
        try:
            prefix = c[3].split("_")[0]+"_"
            column_temp = c[3].split(prefix)[1]
        except:
            column_temp = c[3]

        java_var_detail = {}
        if c[7] == 'integer' or c[7] == 'smallint':
            java_var_detail['type'] = 'int'
            java_var_detail['value'] = column_temp
        elif c[7] == 'character' or c[7] == 'text':
            java_var_detail['type'] = 'String'
            java_var_detail['value'] = column_temp
        elif c[7] == 'timestamp without time zone':
            java_var_detail['type'] = 'Date'
            java_var_detail['value'] = column_temp
        elif c[7] == 'tinyint' or c[7] == 'boolean':
            java_var_detail['type'] = 'boolean'
            java_var_detail['value'] = column_temp
        elif c[7] == 'double precision' or c[7] == 'decimal' or c[7] == 'numeric':
            java_var_detail['type'] = 'double'
            java_var_detail['value'] = column_temp
        else:
            java_var_detail['type'] = 'Object'
            java_var_detail['value'] = column_temp

        java_var_detail['column'] = c[3]

        java_var.append(java_var_detail)

    with open("Modelo/{}.java".format(java_object), "w+") as file:

        file.write('package Model;\n')

        # find in java_var if exist a timestamp without time zone value
        for a in java_var:
            if a['type'] == 'Date':
                file.write('import java.util.Date;\n')
                break

        file.write('\n')
        file.write("public class {}".format(java_object))
        file.write("{\n")

        for a in java_var:
            file.write("\t"+a['type'] + " "+a['value']+";\n")
        file.write('\n')

        java_contructor = "\tpublic {}(".format(java_object)

        c = len(java_var)
        for a in java_var:
            c = c - 1
            java_contructor = java_contructor + \
                "{} {}".format(a['type'], a['value'])
            if c != 0:
                java_contructor = java_contructor+", "

        java_contructor = java_contructor+"){\n"

        for a in java_var:
            java_contructor = java_contructor + \
                "\t\tthis.{} = {};\n".format(a['value'], a['value'])

        java_contructor = java_contructor + "\t}"

        java_contructor2 = "\tpublic {}(int {})".format(
            java_object, java_var[0]['value'])
        java_contructor2 = java_contructor2 + \
            "{\n\t\tthis."+java_var[0]['value']+" = "+java_var[0]['value']+";"
        java_contructor2 = java_contructor2 + "\n\t}"

        file.write(java_contructor)
        file.write('\n')
        file.write(java_contructor2)
        file.write('\n')

        java_toString = '\t@Override\n\tpublic String toString() {\n\t\treturn "' + \
            java_object+'{"'

        for a in java_var:
            java_toString = java_toString + \
                '+", {}=" + {}'.format(a['value'], a['value'])

        java_toString = java_toString + '+"}";\n\n'

        file.write(java_toString)
        file.write("\t}\n")
        java_setter = ""

        for a in java_var:
            java_setter = '\tpublic {} get{}()'.format(
                a['type'], a['value'].capitalize())
            java_setter = java_setter + '{\n'
            java_setter = java_setter + '\t\treturn {};\n'.format(a['value'])
            java_setter = java_setter + '\t}\n'
            file.write(java_setter)

            java_getter = '\tpublic void set{}({} {})'.format(
                a['value'].capitalize(), a['type'], a['value'])
            java_getter = java_getter + '{\n'
            java_getter = java_getter + '\t\tthis.' + \
                a['value']+' = '+a['value']+';\n'
            java_getter = java_getter + '\t}\n'
            file.write(java_getter)

        file.write('\n}')
        file.close()

    with open("DAO/DAO{}.java".format(java_object), "w+") as file:

        dao_head = "package Controler;\n" +\
            "import java.sql.PreparedStatement;\n" +\
            "import java.sql.ResultSet;\n" +\
            "import java.sql.SQLException;\n" +\
            "import java.util.ArrayList;\n" +\
            "import jdbc.DB;\n" +\
            "import javax.swing.JOptionPane;\n"

        file.write(dao_head)

        dao_var = "\npublic class DAO"+java_object+" {\n"
        dao_var = dao_var + "\tprivate " + \
            java_object+" "+java_object[0:4]+";\n"
        dao_var = dao_var + "\tpublic ArrayList<" + \
            java_object+"> resultado"+java_object+";\n\n"

        file.write(dao_var)

        dao_actualizar = '\n\tpublic void actualizar'+java_object+'(String condicion) {' +\
            '\n\t\tresultado'+java_object+' = listar(condicion);\n\t}\n\n'

        file.write(dao_actualizar)

        dao_listar = '\tpublic ArrayList listar(String condicion) {' +\
            '\n\t\ttry {\n\t\t\tDB.conecta();' +\
            '\n\t\t\tString q = "select * from  '+t[0]+' " + condicion + " order by '+java_var[0]['column']+' desc";' +\
            '\n\t\t\tPreparedStatement ps = DB.getCon().prepareStatement(q);' +\
            '\n\t\t\tResultSet rs = ps.executeQuery();\n' +\
            '\n\t\t\tArrayList arr = new ArrayList();\n' +\
            '\n\t\t\twhile (rs.next()) {' +\
            '\n\t\t\t\t'+java_object[0:4]+' = new '+java_object+'('

        c = len(java_var)
        for a in java_var:
            if a['type'] == 'int':
                dao_listar = dao_listar + \
                    '\n\t\t\t\t\t\trs.getInt("'+a['column']+'")'
            elif a['type'] == 'String':
                dao_listar = dao_listar + \
                    '\n\t\t\t\t\t\trs.getString("'+a['column']+'")'
            elif a['type'] == 'double':
                dao_listar = dao_listar + \
                    '\n\t\t\t\t\t\trs.getDouble("'+a['column']+'")'
            elif a['type'] == 'boolean':
                dao_listar = dao_listar + \
                    '\n\t\t\t\t\t\trs.getBoolean("'+a['column']+'")'
            elif a['type'] == 'Object':
                dao_listar = dao_listar + \
                    '\n\t\t\t\t\t\trs.getObject("'+a['column']+'")'
            elif a['type'] == 'Date':
                dao_listar = dao_listar + \
                    '\n\t\t\t\t\t\trs.getTimestamp("'+a['column']+'")'
            c = c - 1
            if c > 0:
                dao_listar = dao_listar + ','

        dao_listar = dao_listar + \
            '\n\t\t\t);\n\t\t\tarr.add(' + \
            java_object[0:4]+');\n\t\t}\n\n\t\t\treturn arr;'
        dao_listar = dao_listar + '\n\t\t} catch (SQLException ex) {'
        dao_listar = dao_listar + \
            '\n\t\t\tSystem.out.println(ex.getMessage());\n\t\t}\n\t\treturn null;\n\t}'

        file.write(dao_listar)
        file.write('\n\n')

        dao_insertar = '\tpublic boolean insertar('+java_object+' '+java_object[0:4]+') {' +\
            '\n\t\tString q = " insert into '+java_object+'('

        sw = 0
        c = len(java_var)
        for a in java_var:
            if c == len(java_var):
                c = c - 1
            else:
                c = c - 1
                dao_insertar = dao_insertar + " "+a['column']
                if c != 0:
                    dao_insertar = dao_insertar+", "

        dao_insertar = dao_insertar + ') values ('
        c = len(java_var)

        for a in java_var:
            if c == len(java_var):
                c = c - 1
            else:
                c = c - 1
                dao_insertar = dao_insertar + '?'
                if c != 0:
                    dao_insertar = dao_insertar+", "

        dao_insertar = dao_insertar + ')";\n' +\
            '\n\t\ttry {\n\t\t\tDB.conecta();' +\
            '\n\t\t\tPreparedStatement ps = DB.getCon().prepareStatement(q);'

        c = 0
        for a in java_var:
            if c > 0:
                if a['type'] == 'int':
                    dao_insertar = dao_insertar + \
                        '\n\t\t\tps.setInt('+str(c)+', ' + \
                        java_object[0:4]+'.get'+a['value'].capitalize()+'());'
                elif a['type'] == 'String':
                    dao_insertar = dao_insertar + \
                        '\n\t\t\tps.setString('+str(c)+', ' + \
                        java_object[0:4]+'.get'+a['value'].capitalize()+'());'
                elif a['type'] == 'double':
                    dao_insertar = dao_insertar + \
                        '\n\t\t\tps.setDouble('+str(c)+', ' + \
                        java_object[0:4]+'.get'+a['value'].capitalize()+'());'
                elif a['type'] == 'boolean':
                    dao_insertar = dao_insertar + \
                        '\n\t\t\tps.setBoolean('+str(c)+', ' + \
                        java_object[0:4]+'.get'+a['value'].capitalize()+'());'
                elif a['type'] == 'Object':
                    dao_insertar = dao_insertar + \
                        '\n\t\t\tps.setObject('+str(c)+', ' + \
                        java_object[0:4]+'.get'+a['value'].capitalize()+'());'
                elif a['type'] == 'Date':
                    dao_insertar = dao_insertar + '''
                     if ([[obj]] != null) {
                            ps.setTimestamp([[c]], new Timestamp([[obj]].getTime()));
                     } else {
                            ps.setNull([[c]], Types.TIMESTAMP);
                     }
                     '''.replace("[[obj]]", java_object[0:4]+".get"+a['value'].capitalize()+"()").replace("[[c]]", str(c))

            c = c + 1

        dao_insertar = dao_insertar + '\n\t\t\tps.executeUpdate();\n\t\t\treturn true;' +\
            '\n\t\t} catch (SQLException ex) {' +\
            '\n\t\t\tJOptionPane.showMessageDialog(null, "Error inesperado: " + ex.getMessage(), "Agregar '+java_object+'", JOptionPane.ERROR_MESSAGE);\n\t\t}' +\
            '\n\t\treturn false;\n\t}'

        file.write(dao_insertar)
        file.write('\n\n')

        dao_modificar = '\tpublic boolean modificar('+java_object+' '+java_object[0:4]+') {' +\
            '\n\t\tString q = " update '+java_object+' set '

        for a in java_var:
            if c == len(java_var):
                c = c - 1
            else:
                c = c - 1
                dao_modificar = dao_modificar + " "+a['column']+"=?"
                if c != 0:
                    dao_modificar = dao_modificar+", "

        dao_modificar = dao_modificar + ' where ' + \
            java_var[0]['column']+'=?";\n'

        dao_modificar = dao_modificar + '\n\t\ttry {\n\t\t\tDB.conecta();' +\
            '\n\t\t\tPreparedStatement ps = DB.getCon().prepareStatement(q);'
        c = 0
        for a in java_var:
            if c > 0:
                if a['type'] == 'int':
                    dao_modificar = dao_modificar + \
                        '\n\t\t\tps.setInt('+str(c)+', ' + \
                        java_object[0:4]+'.get'+a['value'].capitalize()+'());'
                elif a['type'] == 'String':
                    dao_modificar = dao_modificar + \
                        '\n\t\t\tps.setString('+str(c)+', ' + \
                        java_object[0:4]+'.get'+a['value'].capitalize()+'());'
                elif a['type'] == 'double':
                    dao_modificar = dao_modificar + \
                        '\n\t\t\tps.setDouble('+str(c)+', ' + \
                        java_object[0:4]+'.get'+a['value'].capitalize()+'());'
                elif a['type'] == 'boolean':
                    dao_modificar = dao_modificar + \
                        '\n\t\t\tps.setBoolean('+str(c)+', ' + \
                        java_object[0:4]+'.get'+a['value'].capitalize()+'());'
                elif a['type'] == 'Date':
                    dao_insertar = dao_insertar + '''
                     if ([[obj]] != null) {
                            ps.setTimestamp([[c]], new Timestamp([[obj]].getTime()));
                     } else {
                            ps.setNull([[c]], Types.TIMESTAMP);
                     }
                     '''.replace("[[obj]]", java_object[0:4]+".get"+a['value'].capitalize()+"()").replace("[[c]]", str(c))
                elif a['type'] == 'Object':
                    dao_modificar = dao_modificar + \
                        '\n\t\t\tps.setObject('+str(c)+', ' + \
                        java_object[0:4]+'.get'+a['value'].capitalize()+'());'
            c = c + 1

        dao_modificar = dao_modificar + \
            '\n\t\t\tps.setInt('+str(c)+', '+java_object[0:4]+'.getId());'

        dao_modificar = dao_modificar + '\n\t\t\tps.executeUpdate();\n\t\t\treturn true;' +\
            '\n\t\t} catch (SQLException ex) {' +\
            '\n\t\t\tJOptionPane.showMessageDialog(null, "Error inesperado: " + ex.getMessage(), "Modificar '+java_object+'", JOptionPane.ERROR_MESSAGE);\n\t\t}' +\
            '\n\t\treturn false;\n\t}'

        file.write(dao_modificar)
        file.write('\n\n')

        dao_eliminar = '\tpublic boolean eliminar('+java_object+' '+java_object[0:4]+') {' +\
            '\n\t\tString q = " delete from '+java_object+' where id=?";'

        dao_eliminar = dao_eliminar + '\n\t\ttry {\n\t\t\tDB.conecta();' +\
            '\n\t\t\tPreparedStatement ps = DB.getCon().prepareStatement(q);' +\
            '\n\t\t\tps.setInt(1, '+java_object[0:4]+'.getId());' +\
            '\n\t\t\tps.executeUpdate();\n\t\t\treturn true;' +\
            '\n\t\t} catch (SQLException ex) {' +\
            '\n\t\t\tJOptionPane.showMessageDialog(null, "Error inesperado: " + ex.getMessage(), "Eliminar '+java_object+'", JOptionPane.ERROR_MESSAGE);\n\t\t}' +\
            '\n\t\treturn false;\n\t}'

        file.write(dao_eliminar)
        file.write('\n}')

        file.close()

fin = time.time()
print(fin-inicio)
