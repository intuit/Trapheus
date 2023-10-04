<p align="center">
<img width="300" height="280" src="../screenshots/Trapheus.png">
</p>
<p align="center">
<b>Restaurar instancias de RDS en AWS sin preocuparse por el tiempo de inactividad del cliente o la retención de la configuración.</b><br/>
<sub>Trapheus puede restaurar una instancia RDS individual o un clúster RDS.
Modelado como una máquina de estado, con la ayuda de las funciones de pasos de AWS, Trapheus restaura la instancia de RDS de una manera mucho más rápida que el volcado de SQL habitual, conservando el mismo punto final de la instancia y las mismas configuraciones que antes.
</sub>
</p>
<p align="center"><a href="https://circleci.com/gh/intuit/Trapheus"><img src="https://circleci.com/gh/intuit/Trapheus.svg?style =svg" alt="Estado de compilación de TravisCI"/></a>
<a href = "https://coveralls.io/github/intuit/Trapheus?branch=master"><img src= "https://coveralls.io/repos/github/intuit/Trapheus/badge.svg?branch=master" alt = "Cobertura"/></a>
   <a href="http://www.serverless.com"><img src="http://public.serverless.com/badges/v3.svg" alt="insignia sin servidor"/></a>
   <a href="https://github.com/intuit/Trapheus/releases"><img src="https://img.shields.io/github/v/release/intuit/trapheus.svg" alt=" insignia de lanzamiento"/></a>
</p>

<img src="https://ch-resources.oss-cn-shanghai.aliyuncs.com/images/lang-icons/icon128px.png" width="22px" /> [Inglés](README.md) | [简体中文](./docs/README.zh-CN.md) | [francés](./docs/README.fr.md)

- **Importante:** esta aplicación utiliza varios servicios de AWS y existen costos asociados con estos servicios después del uso de la capa gratuita; consulte la [página de precios de AWS](https://aws.amazon.com/pricing/) para obtener más información. detalles.

[![----------------------------------------------- ----------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#table-of-contents)

## Tabla de contenido

- [➤ Prerrequisitos](#prerrequisitos)
- [➤ Parámetros](#parámetros)
- [➤ Instrucciones](#instrucciones)
- [➤ Ejecución](#ejecución)
- [➤ Cómo funciona](#cómo-funciona)
- [➤ Contribuyendo a Trapheus](#contribuyendo-a-trapheus)
- [➤ Colaboradores](#colaboradores)

[![----------------------------------------------- -------------------------------------------------- -------------------------------------------------- ------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#pre-requisitos)

## Requisitos previos

La aplicación requiere que existan los siguientes recursos de AWS antes de la instalación:

1. `python3.7` instalado en la máquina local siguiendo [esto](https://www.python.org/downloads/).

2. Configure [AWS SES](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/event-publishing-create-configuration-set.html)

   - Configurar el correo electrónico del remitente y del destinatario de SES ([Consola SES](https://console.aws.amazon.com/ses/)->Direcciones de correo electrónico).
     - Se configura una alerta de correo electrónico de SES para notificar al usuario sobre cualquier falla en la máquina de estado. El parámetro de correo electrónico del remitente es necesario para configurar el ID de correo electrónico a través del cual se envía la alerta. El parámetro de correo electrónico del destinatario es necesario para configurar el ID de correo electrónico al que se envía la alerta.

3. Cree el depósito S3 donde el sistema almacenará las plantillas de formación de nubes:

   - Nombre propuesto: trapheus-cfn-s3-[id-cuenta]-[región]. Se recomienda que el nombre contenga su:
     - ID de cuenta, ya que los nombres de los depósitos deben ser globales (evita que otra persona tenga el mismo nombre)
     - Región, para realizar un seguimiento fácilmente cuando tienes depósitos Trapheus-s3 en varias regiones.

4. Una VPC (específica de la región). Se debe utilizar la misma VPC/región para las instancias de RDS, que se utilizarán en Trapheus, y las lambdas de Trapheus.

   - Consideración de la selección de la región. Regiones que soportan:
     - [Recepción de correo electrónico](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/regions.html#region-receive-email). Consulte [Parámetros](#parámetros) -> 'Correo electrónico del destinatario' para obtener más información.
   - Ejemplo de configuración mínima de VPC:
     - Consola VPC:
       - nombre: Trapheus-VPC-[región] (especifique la [región] donde se crea su VPC - para realizar un seguimiento fácilmente cuando tenga Trapheus-VPC en varias regiones)
       - [Bloque CIDR IPv4](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html#vpc-sizing-ipv4): 10.0.0.0/16
     - Consola VPC->página Subredes y cree dos subredes privadas:
       - Subred1:
         - VPC: Trapheus-VPC-[región]
         - Zona de disponibilidad: elige una
         - Bloque CIDR IPv4: 10.0.0.0/19
       - Subred2:
         - VPC: Trapheus-VPC-[región]
         - Zona de disponibilidad: elija una diferente a la Subred1 AZ.
         - Bloque CIDR IPv4: 10.0.32.0/19
     - Ha creado una VPC con solo dos subredes privadas. Si está creando subredes no privadas, verifique [la relación entre subredes públicas y privadas, subred privada con ACL de red personalizada dedicada y capacidad adicional](https://aws-quickstart.github.io/quickstart-aws-vpc/) .

5. Una o más instancias de una base de datos RDS que desea restaurar.
   - Ejemplo de configuración RDS mínima _gratuita_:
     - Opciones de motor: MySQL
     - Templo
