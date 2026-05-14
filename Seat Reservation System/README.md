# Seat Reservation System

大学图书馆/自习室座位预约系统。

## 业务规则

- 座位分区域：安静区、讨论区、计算机区
- 预约时段最小 1h，最长 4h
- 预约后 30 分钟内不签到 → 自动取消 + 扣信用分 10 分
- 暂离最长 30 分钟，超时自动释放座位
- 信用分 < 60 → 不能再预约
- 信用分每 30 分钟自动 +1（上限 100）
- 管理员可以设置座位维护状态

## 全局常量

统一在 `src/adapters/model.py` 和 `src/adapters/service.py` 文件头部定义：

| 常量                                    | 值   | 位置       |
| --------------------------------------- | ---- | ---------- |
| REPUTATION_SCORE_MIN                    | 0    | model.py   |
| REPUTATION_SCORE_MAX                    | 100  | model.py   |
| REPUTATION_SCORE_CAN_RESERVATION        | 60   | model.py   |
| RESERVATION_MIN_HOURS                   | 1    | model.py   |
| RESERVATION_MAX_HOURS                   | 4    | model.py   |
| TEMPORARILY_AWAY_MAX_SECONDS            | 1800 | model.py   |
| CHECK_IN_TIMEOUT_SECONDS                | 1800 | service.py |
| TEMPORARILY_AWAY_TIMEOUT_SECONDS        | 1800 | service.py |
| REPUTATION_SCORE_REDUCE_ON_EXPIRE       | 10   | service.py |
| REPUTATION_SCORE_INCREASE_CYCLE_SECONDS | 1800 | service.py |

## 项目结构

```
Seat Reservation System/
├── docs/
│   ├── Class.mmd              # 类图 (Mermaid)
│   ├── ReservationState.mmd   # 预约状态机 (Mermaid)
│   └── ReserveSequence.mmd    # 时序图 (Mermaid)
├── src/
│   ├── main.py                # 入口 & demo
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── exception.py       # 异常层次结构
│   │   ├── model.py           # 领域模型 (Entity / Value Object)
│   │   ├── port.py            # Repository 接口 (ABC)
│   │   └── service.py         # 应用服务层
│   └── domain/
│       ├── __init__.py
│       ├── command.py         # Command 装饰器 (事务回滚)
│       ├── memory_repository.py  # 内存 Repository 实现
│       └── timer.py           # Timer & TimerManager
├── tests/
└── README.md
```

## 架构分层

- **Model 层**：`ReputationScore`、`Student`、`Reservation`、`Seat`、`Position`、`TimePeriod` 等值对象与实体
- **Port 层**：`StudentRepository`、`SeatRepository`、`ReservationRepository` 接口
- **Service 层**：`ReservationService`、`StudentService`、`SeatService`、`StudentSeatReservationService`（业务编排 + Command 装饰事务控制）
- **Infrastructure**：`MemoryStudentRepository`、`MemorySeatRepository`、`MemoryReservationRepository`、`TimerManager`

## 预约状态机

```
[*] → PENDING_CHECK_IN → CHECKED_IN → ENDED
                        → EXPIRED
                        → CANCELLED
CHECKED_IN → TEMPORARILY_AWAY → CHECKED_IN
                               → EXPIRED
```

## 运行 Demo

```bash
PYTHONPATH=src python src/main.py
```
