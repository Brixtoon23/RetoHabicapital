# RetoHabicapital


**Decisiones clave y por qué las tomaste**

La principal clave fue la elección de herramientas. Sin FastAPI y Railway no
hubiera sido posible desarrollar el reto en tan poco tiempo. FastAPI me
permitió construir toda la lógica de endpoints (GET, POST) con validaciones
automáticas y documentación generada casi gratis. Railway fue clave porque me
dejó levantar backend y base de datos al mismo tiempo sin perder tiempo en
configuración.

La segunda decisión importante fue el tipo de
base de datos: usé SQL porque al manejar dinero la prioridad no es velocidad
sino tener un ACID sólido para mantener consistencia.

A nivel de aplicación, otra decisión clave fue
el tipo de dato para dinero: usé BigInteger porque un float puede generar
errores por cómo representa los números. También puse una restricción para que
los montos siempre sean mayores a 0, evitando saldos negativos.

En el feature de “bolsillo”, definí dos
estados: cancelado y resuelto. “Resuelto” cuando se completa y se rompe el
bolsillo para consignar a quien recolecta, y “cancelado” cuando el plan se cae
y el dinero se devuelve automáticamente a cada usuario.

**Qué dejaste fuera y por qué**

Dejé por fuera validaciones de seguridad más robustas. Con más tiempo hubiera
implementado cosas como rate limiting por IP o controles más finos.

No hice un frontend real: solo hay un HTML
plano. La idea sería luego montarlo con algo como React o desplegarlo en
Vercel, pero no era el foco del reto.

También dejé por fuera diagramas UML. Me
gustan porque ordenan mucho, pero hacerlos bien toma tiempo.

Y en general quedaron posibles bugs o edge
cases si los usuarios se ponen creativos.

**Qué harías distinto con más tiempo**

Primero, diseñar mejor el modelo de datos antes de escribir código — tomé
atajos que después tuve que corregir.

Segundo, tests más completos. Tengo casos
básicos, pero faltan pruebas de concurrencia (por ejemplo, dos requests
simultáneos al mismo bolsillo).

Tercero, seguridad: falta rate limiting,
validaciones de montos máximos y mejores logs de auditoría.

Cuarto, un frontend real desplegado, no un
HTML local.

**Qué NO sabes (sí, en serio)**

FastAPI, SQLAlchemy, Alembic y Railway eran nuevos para mí antes de este reto.
Los aprendí durante las 72 horas preguntando y leyendo documentación. La lógica
de programación ya la tenía, así que adaptarme a la sintaxis no fue tan duro,
pero no tengo experiencia real llevando este stack a producción.

Tampoco sé qué tan bien escala esto bajo carga
real. El uso de with_for_update() serializa operaciones sobre la misma cuenta,
y eso podría volverse un cuello de botella con muchos requests simultáneos.

**Supuestos que hiciste y por qué**

Las transferencias se hacen por email del destinatario, porque es más usable
que manejar UUIDs, aunque en producción tocaría mejorar la búsqueda.

El sistema maneja una sola moneda, sin
conversiones.

La autenticación con JWT de 24h es suficiente
para el scope del reto, aunque en producción agregaría refresh tokens y
revocación.

Asumo que los usuarios no se registran dos
veces porque se respeta el estado. Tampoco implementé expiración de bolsillos
por tiempo.

**Cómo usaste IA**

Le conté mi idea y le pedí un esqueleto base para asegurar compatibilidad con
el stack. Luego, mientras avanzaba, lo usé como reviewer: le pasaba código para
ver si tenía sentido o si había mejores formas de hacer cosas.

También lo usé para generar el HTML de
presentación, porque escribirlo a mano es lento y no era el core del reto.

**Qué aprendiste**

Construí una API con autenticación, base de datos relacional y deploy en
producción en menos de 4 horas de código efectivo. Antes eso me sonaba a
proyecto de semanas, así que me cambió completamente la referencia de lo que es
posible.

El choque más grande fue pasar de problemas de
la u con enunciado claro y una estructura y stack definido, a un problema
abierto donde yo decido qué construir. Acá no solo importa el código, sino las
decisiones.

Realmente
me sorprendió mucho como pude crear algo con ayuda de la ia tan rápido. Me
emociona trabajar con una empresa que lo tome como su c
