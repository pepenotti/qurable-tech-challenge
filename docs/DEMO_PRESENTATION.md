---
marp: true
theme: default
paginate: true
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
---

<!-- _class: lead -->

# 🎫 Servicio de Cupones (Coupon Book)

### Implementación Completa del Desafío Técnico

**Desafío**: Diseñar API + Pseudocódigo + Arquitectura  
**Entregado**: Aplicación funcionando completamente

**Construido con**: FastAPI • Vue 3 • PostgreSQL • Docker

---

## 🚀 Preparación para Producción & Opciones de Deployment

### Enfoques de Deployment

**1. Monolítico (Inicio Simple)**
- ECS Fargate o AWS App Runner
- RDS PostgreSQL Multi-AZ
- CloudFront + S3 para frontend
- ✅ Simple, cost-effective, maneja carga significativa

**2. Microservicios (Escala & Equipos)**
- Auth Service + Coupon Service + Redemption Service
- Scaling y deployment independientes
- Comunicación event-driven (SQS/EventBridge)
- ✅ Mejor para organizaciones grandes, equipos independientes

**3. Serverless (Carga Variable)**
- Lambda functions + API Gateway
- Aurora Serverless o DynamoDB
- Auto-scale a cero, pago por request
- ✅ Perfecto para tráfico con picos, ops mínimas

**Adiciones para Producción** (cualquier enfoque):
- Métricas de CloudWatch & tracing con X-Ray
- Secrets Manager para credenciales
- Rate limiting & protección DDoS
- Backups de database & plan de DR

**La arquitectura es deployment-agnostic** - boundaries limpios permiten cualquier modelo 🎯

---

## 📋 El Desafío

**Lo que se pidió**: Diseño de API + pseudocódigo + arquitectura

**Requerimientos Core**:
- ✅ Coupon books con upload/generación de códigos
- ✅ Asignación random de cupones con manejo de concurrencia
- ✅ Mecanismo de lock para redención
- ✅ Soporte multi-redención (a nivel de book)
- ✅ Máximo de asignaciones por usuario (a nivel de book)

**Desafíos Técnicos Clave**:
1. Locking de database y manejo de estado
2. Lógica de randomness bajo carga concurrente
3. Prevenir race conditions e integridad de datos

**Lo que entregué**: Implementación completamente funcionando (no solo docs de diseño) ⭐

---

## 🛠️ Tech Stack

| Capa | Tecnología | ¿Por qué? |
|-------|-----------|------|
| **Backend** | FastAPI + Python 3.11 | Async/await, docs automáticos, type safety |
| **Database** | PostgreSQL 15 | ACID, advisory locks, row locking |
| **ORM** | SQLAlchemy 2.0 (async) | Patrones async modernos |
| **Frontend** | Vue 3 + Pinia | Reactivo, liviano, moderno |
| **Infraestructura** | Docker Compose | Ambientes consistentes |

**Cada elección fue deliberada** - optimizado para concurrencia, integridad de datos y developer experience.

---

## 🏗️ Resumen de Arquitectura

![Architecture Diagram](./diagrams/exported/png/System%20Architecture.png)

**Diseño de 3 Capas**:
- Frontend: Vue 3 SPA
- Backend: FastAPI con servicios async
- Data: PostgreSQL con connection pooling

**Flexibilidad de Deployment**:
- 📦 **Monolítico**: ECS/App Runner (simple, cost-effective)
- 🔷 **Microservicios**: Auth, coupon y redemption services separados
- ⚡ **Serverless**: Lambda + API Gateway + Aurora Serverless

**Principio Clave**: Stateless, servicios separados, deployment-agnostic

---

## 🗄️ Schema de Database

![Database Schema](./diagrams/exported/png/Database%20Schema.png)

---

## 📊 Schema de Database (Detalle)

**6 Tablas**:
- **Users**: Autenticación (JWT, bcrypt, roles)
- **Books**: Configuración de coupon books
- **Coupons**: Core del state machine (14 campos)
- **RedemptionHistory**: Audit trail
- **UserPools**: Grupos de distribución bulk
- **pool_users**: Asociación many-to-many

**Highlights de Diseño**:
- Indexes apropiados en foreign keys y estado
- DELETE CASCADE donde corresponde
- JSONB para metadata flexible

---

## 🔄 State Machine

![State Machine](./diagrams/exported/png/State%20Machine.png)

---

## 🔄 State Machine (Explicado)

```
UNASSIGNED → ASSIGNED → LOCKED → REDEEMED
              ↑           ↓
              └───────────┘ (unlock on timeout)
```

**Transiciones Clave**:
- **Assign**: Reclamar un cupón (con validación)
- **Lock**: Preparar para canje (timeout 5 min)
- **Redeem**: Finalizar (permanente, logged)
- **Unlock**: Timeout automático (previene deadlocks)

**Cada transición es validada** - previene todos los edge cases

---

## ✨ Features Clave

### Requeridos (Specs del Desafío)
- 🎲 **Asignación Random** - Con SELECT FOR UPDATE SKIP LOCKED
- ♻️ **Multi-Redención** - Configurable por book
- 🔢 **Max Asignaciones** - Por usuario, por book
- 📤 **Upload/Generación de Códigos** - Upload CSV o basado en pattern
- 🔒 **Mecanismo de Lock** - Lock temporal antes de canjear
- 🔄 **State Machine** - UNASSIGNED → ASSIGNED → LOCKED → REDEEMED

### Bonus (Adiciones de Producción)
- 🔐 **Autenticación JWT** - Acceso basado en roles (ADMIN/USER)
- 🎨 **Frontend Vue 3** - Implementación completa de UI
- 📦 **User Pools** - Distribución bulk (modos equal/random)
- 📝 **Audit Trail** - Historial completo de canjes
- ✅ **Test Suite** - Scripts de validación comprehensivos

**De doc de diseño a producto funcionando** 🚀

---

## 📊 Requerimientos del Desafío vs Entrega

| Requerimiento | Se Pidió | Entregado |
|------------|-----------|-----------|
| System Architecture | Diseño high-level | ✅ + Diagramas detallados |
| Database Design | Schema high-level | ✅ + Implementación completa |
| API Endpoints | Diseño + formatos | ✅ + FastAPI funcionando |
| Pseudocódigo | 3 operaciones clave | ✅ + Código de producción |
| Deployment Strategy | Plan high-level | ✅ + Docker + docs AWS |
| **Frontend** | ❌ No requerido | ✅ App Vue 3 completa |
| **Autenticación** | ❌ No especificado | ✅ JWT + RBAC |
| **Testing** | ❌ No requerido | ✅ Test suite |
| **Documentación** | Básica | ✅ 11 docs + 8 diagramas |

**Convertí un ejercicio de diseño en un demo production-ready** 💪

---

## ⚡ Solución de Concurrencia

**El Problema**: 1000 usuarios, 100 códigos restantes. Sin duplicados. Sin race conditions.

**La Solución**:
```python
# PostgreSQL advisory locks + SKIP LOCKED
async with session.begin():
    # 1. Adquirir lock a nivel de book (advisory lock)
    await session.execute(text("SELECT pg_advisory_lock(:book_id)"), 
                          {"book_id": book_hash})
    
    # 2. SELECT FOR UPDATE SKIP LOCKED
    coupon = await session.execute(
        select(Coupon)
        .where(Coupon.book_id == book_id, Coupon.state == 'UNASSIGNED')
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    
    # 3. Asignar atómicamente
    coupon.state = 'ASSIGNED'
    coupon.assigned_user_id = user_id
```

**Resultado**: Escala perfectamente bajo carga concurrente 🚀

---

## 🧪 Demo de Concurrencia

![Sequence Diagram](./diagrams/exported/png/Assign%20Random%20Coupon.png)

**Validado con scripts de test concurrentes** - 100 requests simultáneos ✅

---

## 💻 Highlights de la API

**Patrones Modernos de Python**:
- ✅ Async/await en todas partes
- ✅ Pydantic para validación
- ✅ Service layer para business logic
- ✅ Excepciones custom → códigos HTTP
- ✅ Mensajes de error comprehensivos
- ✅ Docs OpenAPI en `/docs`

**Calidad de Código**:
- Type hints en todo
- Separación limpia de concerns
- Testeable y mantenible

---

## 🎨 Demo del Frontend

**¡Momento de Demo en Vivo!** 

**Flujo**:
1. Login como admin
2. Crear un coupon book
3. Upload de códigos (CSV)
4. Distribuir a user pool
5. Cambiar a cuenta de usuario
6. Lockear y canjear cupón

**Features de UX**:
- Notificaciones toast (non-blocking)
- Updates de estado en tiempo real
- Timers de countdown para locks
- Feedback con código de colores

---

## ✅ Testing & Calidad

**Cobertura de Tests**:
- `showcase_tests.sh` - Tests de integración comprehensivos
- Simulación de requests concurrentes
- Validación de casos de error
- Edge cases del state machine

**Manejo de Errores**:
- Excepciones de database → mensajes user-friendly
- Validación antes de hits a DB
- Respuestas de error accionables

**Documentación**:
- 8 diagramas PlantUML
- READMEs comprehensivos
- Documentación inline en código

---

## 🎓 Lecciones Aprendidas

**Insights Técnicos**:
1. Los features de concurrencia de PostgreSQL son increíblemente poderosos
2. Los state machines hacen la business logic bulletproof
3. Las capacidades async de FastAPI brillan en workloads de I/O
4. Buena documentación = buen código

**Lo que Mejoraría**:
- Agregar logging comprehensivo desde el inicio
- Setup de CI/CD desde el día uno
- Considerar Redis para locking distribuido
- Agregar más unit tests en el frontend

---

## 🚀 Preparación para Producción

**Infraestructura** (Lista para deploy):
- AWS ECS Fargate (backend)
- RDS PostgreSQL Multi-AZ (database)
- CloudFront + S3 (frontend)
- Application Load Balancer

**Aún Necesario**:
- Métricas & logs de CloudWatch
- AWS Secrets Manager
- Rate limiting
- SSL everywhere
- Backups de database
- Plan de disaster recovery

**La parte difícil (business logic) está hecha** ✅

---

## 📊 Métricas del Proyecto

**Código**:
- Backend: ~3,000 líneas de Python
- Frontend: ~2,000 líneas de Vue/TypeScript
- Database: 6 tablas, 8 relaciones
- API: 20+ endpoints

**Documentación**:
- 11 archivos markdown (organizados)
- 8 diagramas PlantUML
- Getting started guide comprehensivo

**Inversión de Tiempo**: [X horas]
- Implementación: [Y%]
- Testing & Polish: [Z%]
- Documentación: [W%]

---

<!-- _class: lead -->

## 🙏 ¡Gracias!

### ¿Preguntas?

**GitHub**: [Tu link de repo]
**Email**: [Tu email]

**Pruébalo vos mismo**:
```bash
git clone [repo]
cd qble/coupon-service
docker-compose up -d
cd frontend && npm install && npm run dev
# Abrir http://localhost:5173
```

**Listo en menos de 5 minutos** 🚀

---

## 📚 Slides de Backup

(Detalles técnicos adicionales si son necesarios)

---

## Detalle del Flujo de Canje

![Redeem Coupon](./diagrams/exported/png/Redeem%20Coupon.png)

**Pasos Clave**:
1. Validar ownership del lock
2. Chequear expiración del lock
3. Verificar contador de canjes
4. Actualizar estado atómicamente
5. Log a RedemptionHistory
6. Commit o rollback

---

## Arquitectura de Deployment en AWS

![AWS Deployment](./diagrams/exported/png/AWS%20Deployment.png)

**Setup de Producción**:
- Backend con auto-scaling
- Database Multi-AZ
- Monitoring con CloudWatch
- Seguridad VPC

---

<!-- _class: lead -->

# ¿Preguntas?

Estoy disponible para profundizar en cualquier aspecto:
- Decisiones de arquitectura
- Detalles de implementación
- Trade-offs y alternativas
- Consideraciones de scaling
- Deployment a producción
