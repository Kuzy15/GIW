# -*- coding: utf-8 -*-

# GESTION DE LA INFORMACIÓN EN LA WEB
# Curso 2017-2018
# Práctica: MongoEngine

# Víctor Fernández Rubio
# David González Jiménez
# Carlos Llames Arribas
# Marta Pastor Puente

# Víctor Fernández Rubio, David González Jiménez, Carlos Llames Arribas y
# Marta Pastor Puente declaramos que esta solución
# es fruto exclusivamente de nuestro trabajo personal. No hemos sido
# ayudados por ninguna otra persona ni hemos obtenido la solución de
# fuentes externas, y tampoco hemos compartido nuestra solución con
# nadie. Declaramos además que no hemos realizado de manera deshonesta
# ninguna otra actividad que pueda mejorar nuestros resultados
# ni perjudicar los resultados de los demás.

from mongoengine import *

class Producto(Document):
    codigo_de_barras = StringField(required=True, unique=True, regex="^\d{13}$")
    nombre = StringField(required=True)
    categoria = IntField(required=True, min_value=0)
    lista_de_categorias = ListField(IntField(min_value=0))

    # Comprobamos que el codigo de barras EAN-13 de un producto esta bien formado,
    # incluyendo su digito de control. Ademas, si un producto tiene categorias
    # secundarias, su categoria principal debe aparecer en el primer lugar de esa
    # lista:
    def clean(self):
        # La comprobación de que tiene 13 digitos se realiza en la declaración
        # del campo mediante una sentencia regex.

        # El digito de control se encuentra en la ultima posicion.
        digito_de_control = int(self.codigo_de_barras[12])

        parcial = 0
        # La funcion enumerate() devuelve un par de valores que corresponden a la
        # posicion dentro del objeto sobre el que iteramos y que pasamos como
        # parametro a la funcion, y el valor que tiene dicha posicion.
        for pos, digito_actual in enumerate(self.codigo_de_barras[:12]):
            # Si la posicion del digito a evaluar es impar, multiplicamos el valor
            # del digito * 1
            if pos % 2 == 0:
                parcial += int(digito_actual)
            # Si la posicion es par, multiplicamos el valor del digito * 3
            else:
                parcial += int(digito_actual) * 3

        digito_calculado = (10 - (parcial % 10)) % 10
        if digito_calculado != digito_de_control:
            raise ValidationError("El digito de control EAN-13 no se corresponde al correcto para el ISBN introducido.")

        # Comprobamos que se cumple la condicion de pertenencia en la primera
        # posicion de la lista de categorias. Como la lista de categorias es
        # opcional, en caso de no existir no devuelve error:
        if self.lista_de_categorias and (self.lista_de_categorias[0] != self.categoria):
            raise ValidationError("La categoria principal del producto no se encuentra en la primera posicion de su lista de categorias secundarias.")


class LineasDePedido(EmbeddedDocument):
    cantidad = IntField(required=True)
    precio_producto = FloatField(required=True, min_value=0.0)
    nombre_producto = StringField(required=True)
    precio_linea = FloatField(required=True, min_value=0.0)
    producto = ReferenceField(Producto, required=True)

    # Comprobamos que el nombre del producto de una linea de pedido es el mismo
    # que el del producto al que apunta la referencia. Además, Ee precio total
    # de una linea de pedido debe estar correctamente calculado en base al precio
    # del producto y la cantidad de ese producto comprados:
    def clean(self):
        # Para referirse a campos de objetos anidados, se usa el doble subrayado __
        # Para referises a campos de objetos referenciados, se usa el punto .
        if self.nombre_producto != self.producto.nombre:
            raise ValidationError("El nombre del producto para la linea de pedido actual no corresponde con el nombre del producto al que referencia.")

        if (float(self.cantidad) * float(self.precio_producto)) != float(self.precio_linea):
            raise ValidationError("El precio total guardado de la linea no corresponde con el total calculado en base al precio del producto y la cantidad pedida.")


class Pedido(Document):
    precio_total = FloatField(required=True)
    fecha = ComplexDateTimeField(required=True)
    lineas_de_pedido = EmbeddedDocumentListField(LineasDePedido, required=True)

    # Comprobamos que el precio total de una linea de pedido esta correctamente
    # calculado en base al precio de un producto y la cantidad de productos
    # comprados:
    def clean(self):
        parcial = 0.0
        for linea in list(self.lineas_de_pedido):
            parcial += float(linea.precio_linea)

        if float(self.precio_total) != parcial:
            raise ValidationError("El precio total guardado del pedido no corresponde con la suma total de todas sus lineas de pedido.")


class TarjetaDeCredito(EmbeddedDocument):
    nombre_completo = StringField(required=True)
    numero = StringField(required=True, regex="^(\d{16})$")
    mes = StringField(required=True, regex="^(0[1-9]|1[0-2])$")
    anio = StringField(required=True, regex='^\d{2}$')
    cvv = StringField(required=True, regex='^\d{3}$')


class Usuario(Document):
    dni = StringField(required=True, unique=True, regex="^(([X-Z]{1})(\d{7})([A-Z]{1}))|((\d{8})([A-Z]{1}))$")
    nombre = StringField(required=True)
    primer_apellido = StringField(required=True)
    segundo_apellido = StringField()
    fecha_de_nacimiento = StringField(required=True, regex='^([0-9]{4})([-])([0-9]{2})([-])([0-9]{2})$')
    ultimos_accesos = ListField(ComplexDateTimeField)
    tarjetas_de_credito = EmbeddedDocumentListField(TarjetaDeCredito)
    pedidos = ListField(ReferenceField(Pedido, reverse_delete_rule=PULL))

    # En el campo pedidos, la opción reverse_delete_rule esta marcada como PULL,
    # lo que implica que cuando un pedido se elimina, este desaparece de la lista
    # de pedidos del usuario que lo realizo.

    # Comprobamos que el formato del DNI de los usuarios es correcto, incluyendo
    # el digito de control:
    def clean(self):
        letras = ['T', 'R', 'W', 'A', 'G', 'M', 'Y', 'F', 'P', 'D', 'X', 'B', 'N',
        'J', 'Z', 'S', 'Q', 'V', 'H', "L", 'C', 'K', 'E']

        if self.dni[0].isdigit(): # Si empieza por numero se trata de formato NIF
            # Verificar el NIF de españoles residentes mayores de edad:
            if self.dni[:8].isdigit() and (letras[int(self.dni[:8]) % 23] != self.dni[8]):
                raise ValidationError(u"La letra del NIF no se corresponde con el numero de control esperado.")
        else: # Si empieza por letra se trata de formato NIE
            # Verificar el NIE de extranjeros residentes en España:
            if self.dni[0] == 'X':
                v = '0'
            elif self.dni[0] == 'Y':
                v = '1'
            elif self.dni[0] == 'Z':
                v = '2'

            if self.dni[1:8].isdigit() and (letters[int(v + self.dni[1:8]) % 23] != self.dni[8]):
                raise ValidationError(u"La ultima letra del NIE no se corresponde con el numero de control esperado.")


def insertar():
    print("EJECUTANDO LA FUNCION insertar() ... ")

    # Insercion de productos correctos que cumplen las resctricciones pedidas:
    pr1 = Producto(codigo_de_barras="1237894563215", nombre="macbook_pro_13", categoria=1, lista_de_categorias=[1, 3, 5])
    pr2 = Producto(codigo_de_barras="7351982406735", nombre="iphone_7_plus", categoria=3, lista_de_categorias=[3, 1, 5])
    pr3 = Producto(codigo_de_barras="1122334455666", nombre="camisa_seda_negra", categoria=16, lista_de_categorias=[16, 10, 12, 14])
    pr4 = Producto(codigo_de_barras="4624768392045", nombre="gorro_lana_cuadros", categoria=18, lista_de_categorias=[])

    pr1.save()
    pr2.save()
    pr3.save()
    pr4.save()

    # Insercion de lineas de pedido correctas que cumplen las resctricciones pedidas:
    lp1 = LineasDePedido(cantidad=1, precio_producto=1099, nombre_producto="macbook_pro_13", precio_linea=1099, producto=pr1)
    lp2 = LineasDePedido(cantidad=1, precio_producto=799, nombre_producto="iphone_7_plus", precio_linea=799, producto=pr2)
    lp3 = LineasDePedido(cantidad=2, precio_producto=54.95, nombre_producto="camisa_seda_negra", precio_linea=109.90, producto=pr3)
    lp4 = LineasDePedido(cantidad=50, precio_producto=12.95, nombre_producto="gorro_lana_cuadros", precio_linea=647.5, producto=pr4)

    # Insercion de pedidos correctos que cumplen las resctricciones pedidas:
    pd1 = Pedido(precio_total=1898, fecha="2017,06,20,18,32,10,888182", lineas_de_pedido=[lp1, lp2])
    pd2 = Pedido(precio_total=757.4, fecha="2017,08,21,13,15,02,888333", lineas_de_pedido=[lp3, lp4])
    pd3 = Pedido(precio_total=1898, fecha="2017,12,01,10,53,27,888216", lineas_de_pedido=[lp1, lp2])
    pd4 = Pedido(precio_total=757.4, fecha="2017,12,08,17,21,33,888229", lineas_de_pedido=[lp3, lp4])
    pd5 = Pedido(precio_total=1746.5, fecha="2017,12,09,07,58,10,888216", lineas_de_pedido=[lp1, lp4])
    pd6 = Pedido(precio_total=908.9, fecha="2017,12,10,22,12,06,888108", lineas_de_pedido=[lp2, lp3])

    pd1.save()
    pd2.save()
    pd3.save()
    pd4.save()
    pd5.save()
    pd6.save()

    # Insercion de tarjetas de credito correctas que cumplen las resctricciones pedidas:
    tc1 = TarjetaDeCredito(nombre_completo='Ignacio Felipe Rode', numero='1592301746920713', mes='02', anio='23', cvv='331')
    tc2 = TarjetaDeCredito(nombre_completo='Celia Segade Quintas', numero='4174856920458820', mes='10', anio='21', cvv='042')
    tc3 = TarjetaDeCredito(nombre_completo='Marta Pastor Puente', numero='5531847930178456', mes='10', anio='21', cvv='472')
    tc4 = TarjetaDeCredito(nombre_completo='Marta Pastor Puente', numero='4022165789374055', mes='06', anio='23', cvv='649')

    # Insercion de usuarios correctos que cumplen las resctricciones pedidas:
    us1 = Usuario(dni='71534484E', nombre='Ignacio', primer_apellido='Felipe', segundo_apellido='Rode', fecha_de_nacimiento='1996-02-17', tarjetas_de_credito=[tc1], pedidos=[pd1, pd2])
    us2 = Usuario(dni='53321817C', nombre='Celia', primer_apellido='Segade', segundo_apellido='Quintas', fecha_de_nacimiento='1993-09-03', tarjetas_de_credito=[tc2], pedidos=[pd5, pd6])
    us3 = Usuario(dni='71475686N', nombre='Marta', primer_apellido='Pastor', segundo_apellido='Puente', fecha_de_nacimiento='1996-08-21', tarjetas_de_credito=[tc3, tc4], pedidos=[pd3, pd4])

    us1.save()
    us2.save()
    us3.save()


    ################################

    print("Insercion de elementos incorrectos a proposito para comprobar el correcto funcionamiento de las restricciones implementadas ... ")


    # Insercion de productos incorrectos que no cumplen las resctricciones pedidas:
    pr5 = Producto(codigo_de_barras="4482710978306", nombre="gorro_lana_rayas", categoria=18, lista_de_categorias=[])
    pr6 = Producto(codigo_de_barras="2759301185937", nombre="perfume_calvin_klein", categoria=59, lista_de_categorias=[13, 21, 59])

    # Insercion de lineas de pedido incorrectas que no cumplen las resctricciones pedidas:
    lp5 = LineasDePedido(cantidad=3, precio_producto=54.95, nombre_producto="camisa_seda_negra", precio_linea="109.90", producto=pr3)
    lp6 = LineasDePedido(cantidad=50, precio_producto=12.95, nombre_producto="gorro_lana_puntos", precio_linea="647.5", producto=pr4)

    # Insercion de pedidos incorrectos que no cumplen las resctricciones pedidas:
    pd7 = Pedido(precio_total=1298, fecha="2017,06,20,18,32,10,888182", lineas_de_pedido=[lp1, lp2])

    # Insercion de usuarios incorrectos que no cumplen las restricciones pedidas:
    us4 = Usuario(dni='72819453T', nombre='Juan Antonio', primer_apellido='Calero', segundo_apellido='Bosque', fecha_de_nacimiento='1999-01-13', tarjetas_de_credito=[], pedidos=[pd3, pd4])

    # pr5.save()
    # pr6.save()
    # pd7.save()
    # us4.save()

    ################################

    print("Borrado de un pedido para comprobar que efectivamente se borra de la lista de pedidos del usuario que lo realizo ... ")

    numero_pedidos = len(Usuario.objects.get(nombre="Marta").pedidos)
    print("Numero de pedidos de Marta antes de borrarlo:", numero_pedidos)
    pd4.delete()
    numero_pedidos = len(Usuario.objects.get(nombre="Marta").pedidos)
    print("Numero de pedidos de Marta despues de borrarlo:", numero_pedidos)


if __name__ == "__main__":
    db = connect('giw_mongoengine')
    db.drop_database('giw_mongoengine')

    insertar()
