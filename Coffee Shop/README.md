# ☕ Coffee Shop — 咖啡店管理系统

这是我第一次尝试**六边形架构（Ports & Adapters）** 的练习项目。  
整个代码是通过**人机协作**的方式完成的——我负责架构设计、决策和评审，AI（Deepseek）负责代码实现。

---

## 项目结构

```
Coffee Shop/
├── docs/                    # 架构文档
│   ├── Class.mmd            # 完整类图
│   ├── ER.mmd               # 数据库ER图
│   ├── CoffeeMachineState.mmd  # 咖啡机状态机
│   ├── OrderState.mmd       # 订单状态机
│   └── Sequence.mmd         # 核心时序图
├── src/
│   ├── main.py              # 程序入口
│   ├── adapters/            # 适配器层（六边形架构的内层）
│   │   ├── __init__.py
│   │   ├── model.py         # 领域模型（枚举 + 数据类）
│   │   ├── ports.py         # 抽象接口（Ports）
│   │   ├── service.py       # 业务逻辑
│   │   └── exception.py     # 自定义异常
│   └── domain/              # 领域层（六边形架构的外层适配）
│       ├── __init__.py
│       ├── repository_memory.py  # 内存版数据仓库
│       ├── repository_mysql.py   # MySQL版（预留，未实现）
│       ├── view_model.py    # 视图模型层
│       └── view.py          # CLI 终端视图
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_exception.py    # 异常测试（9 个）
│   ├── test_repository.py   # 仓库测试（15 个）
│   ├── test_service.py      # 服务测试（19 个）
│   └── test_view_model.py   # 视图模型测试（20 个）
├── pyproject.toml
├── pyrightconfig.json
└── README.md
```

---

## 功能

| 菜单  | 功能          | 说明                                                             |
| ----- | ------------- | ---------------------------------------------------------------- |
| `[1]` | ☕ 制作咖啡   | 选咖啡机 → 选种类 → 输入姓名/时间 → 自动创建订单 + 扣豆 + 倒计时 |
| `[2]` | 📋 查看订单   | 列出所有订单及状态                                               |
| `[3]` | 🌱 添加咖啡豆 | 为指定咖啡机加豆（上限 500g）                                    |
| `[4]` | 🔛 开机       | 唤醒休眠中的咖啡机                                               |
| `[5]` | 🔌 休眠       | 让咖啡机进入休眠                                                 |
| `[6]` | 🧹 清理咖啡机 | 连续计数归零                                                     |
| `[7]` | ✅ 完成订单   | 取餐确认（制作中的订单不可完成）                                 |
| `[0]` | 🚪 退出       |                                                                  |

### 咖啡机状态机

```
IDLE ──点单──→ WORKING ──制作完成──→ IDLE
IDLE ──故障──→ FAULT ──修复──→ IDLE
IDLE ──闲置30分──→ HIBERNATION ──唤醒──→ IDLE
```

### 订单状态机

```
待制作 ──开始制作──→ 制作中 ──完成──→ 待取餐 ──取餐──→ 已完成
待制作 ──取消──→ 已取消
制作中 ──故障/取消──→ 已取消
```

> 注意：制作中的订单不可完成，需等待倒计时结束变为"待取餐"后才能完成。

---

## 技术栈

- Python 3.12+
- pytest + pytest-cov + pytest-asyncio
- 纯内存运行，无外部数据库依赖

---

## 快速开始

```bash
git clone https://github.com/SumengQAQ/system-design.git
cd Coffee\ Shop
python -m venv .venv
source .venv/bin/activate
pip install pytest pytest-cov pytest-asyncio
python src/main.py
```

运行测试：

```bash
python -m pytest tests/ -v
```

查看覆盖率：

```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

---

## 人机合作过程

这个项目是我（人类）和 Deepseek（AI）协作完成的。以下是完整的对话历程：

### 第一阶段：我画架构图，AI 写骨架

我画了完整的 UML 架构图（`docs/Class.mmd`），定义了：

- 领域模型：`CoffeeMachine`、`Order`、各种枚举
- 抽象接口：`CoffeeMachineRepository`、`OrderRepository`
- 业务服务：`CoffeeMachineService`、`OrderService`
- 视图模型 + CLI 视图
- 9 个自定义异常

Claude 根据架构图**生成了所有文件的代码骨架**——类结构、方法签名、import 关系，但所有方法体都是 `...`。

### 第二阶段：我要求补全实现 → 发现并修复问题

我要求 Claude 补全方法实现（只做内存 + 终端版本），过程中发现了多个问题：

**问题 1：`save` 语义冲突**

- 架构图写的是 `save`（新增），但 Service 层修改对象后也需要 `save`
- 解决：改成 **upsert**（存在则覆盖，不存在则新增）

**问题 2：`Order.id` 默认值错误**

- 原始代码 `id: int = -1` 导致自增 ID 永远不触发
- 解决：改成 `id: int | None = None`

**问题 3：pytest 类变量污染**

- `_storage` 和 `_next_id` 作为类变量，测试间互相影响
- 解决：改成实例变量，在 `__init__` 中初始化

**问题 4：`adapters` vs `src.adapters` 模块重复加载**

- `pythonpath=["src"]` 导致 Python 把 `adapters` 和 `src.adapters` 当成两个不同的模块
- 异常跨模块时 `pytest.raises` 匹配不上
- 解决：统一 import 风格 + 去掉 `pythonpath`，改用 `pyrightconfig.json` 的 `extraPaths`

### 第三阶段：我发现的 bug

**Bug：制作中完成订单导致状态错乱**

- 场景：制作咖啡（20秒）→ 在倒计时结束前完成订单 → 咖啡机卡在 WORKING（黄色），订单从 COMPLETED 被异步回调覆盖为 AWAITING_PICKUP
- 根本原因：异步倒计时回调没有校验订单当前状态 + 完成订单没有阻止制作中的订单
- 解决：`OrderViewModel.finish` 加入 `IN_PRODUCTION` 校验，制作中不可完成

**Bug：缺少清洁功能**

- 架构图提到了"连续5杯提醒清理"，但只有提醒没有清理方法
- 解决：新增 `clean()` 方法（Service → ViewModel → View），连续计数归零

### 第四阶段：测试完善

最终实现了 **64 个测试用例**，覆盖：

- 异常：所有 9 个自定义异常的构造和消息
- 仓库：CRUD、upsert、自增 ID、不存在处理、副本隔离
- 服务：状态机校验、库存校验、异常路径、清洁功能
- 视图模型：异步流程、订单状态流转、清洁提醒阈值、回调绑定、边界条件

### 合作心得

1. **架构图是核心契约**——AI 根据图生成代码，我根据图评审代码，减少沟通成本
2. **AI 写代码快但容易忽视细节**（比如类变量污染、默认值错误）——需要人来 review
3. **测试是安全网**——每次修改后跑测试，确保没有回归
4. **发现问题 → 修复 → 加测试 → 更新架构图**——这是整个迭代循环
5. **需要额外的文档来约束业务流程**

---

## 后续可能的拓展

- [ ] MySQL 持久化（`repository_mysql.py` 已预留）
- [ ] 扫码录入咖啡机序列号
- [ ] 一个订单多杯咖啡（需要中间表）
- [ ] 异步日志（loguru）
- [ ] 咖啡豆随时间消耗（非瞬间扣豆）
- [ ] GUI 界面（PyQt / Web）
- [ ] 咖啡种类从数据库读取（而非硬编码 Enum）

---

## License

MIT
