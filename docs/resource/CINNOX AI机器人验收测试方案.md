# CINNOX / M800 前台IM智能机器人

# 验收测试标准（UAT）

## 一、验收目标

验证机器人是否能：

1.  正确识别客户类型（新客户 / 现有客户 / 合作伙伴）

2.  正确触发资料收集流程

3.  正确调用知识库（官网、手册、定价）

4.  正确区分“产品咨询”与“账号问题”

5.  正确转人工

6.  回答准确率达到合同要求

7.  无幻觉报价

8.  无伪造功能

## 二、知识来源范围（测试基准数据）

机器人知识库来源限定为：

线上资源：

1.  docs.cinnox.com（官方用户手册）

2.  cinnox.com（官网）

3.  m800.com（官网）

4.  m800.com/pricing（国际号码与费率）

线下文件：

5.  AI Sales Bot\AI Sales Bot Charging Model.pdf

6.  AI Sales Bot\EN_AI_Sales_Bot_Feature_List_v2026.xlsx

7.  AI Sales Bot\M800 AI-Powered-Sales-Voice-Bot - V 202510 - Basic for EB+IB - EN Ver.pdf

8.  CINNOX\EN_CINNOX_Feature_List_v2026.xlsx

9.  CINNOX\EN_CINNOX_Pricing_07012024_v3.xlsx

10. CINNOX\M800 Introduction - V 202602 - Basic for EB+IB - EN Ver.pdf

11. Global Telecom\M800 VN, Call and SMS Rates.xlsx

12. Global Telecom\M800_Global_Telecom_2026.pdf

若回答内容超出上述资料范围且无依据 → 判定为失败（幻觉）

## 三、整体通过标准

|                    |              |
|:------------------:|:------------:|
|      **项目**      | **合格标准** |
|   意图识别准确率   |    ≥ 90%     |
| 客户身份识别准确率 |    ≥ 95%     |
|   资料收集完整率   |     100%     |
|     报价准确率     |     100%     |
|   功能描述准确率   |    ≥ 95%     |
|       幻觉率       |      0%      |
|    错误转人工率    |     ≤ 5%     |
|    平均响应时间    |    ≤ 3秒     |

## 四、核心测试场景与Test Case

### A. 客户类型识别测试

<table>
<colgroup>
<col style="width: 7%" />
<col style="width: 13%" />
<col style="width: 21%" />
<col style="width: 39%" />
<col style="width: 17%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: center;"><strong>测试编号</strong></td>
<td style="text-align: center;"><strong>测试名称</strong></td>
<td style="text-align: center;"><strong>输入（例子）</strong></td>
<td style="text-align: center;"><strong>预期行为/结果</strong></td>
<td style="text-align: center;"><strong>失败标准</strong></td>
</tr>
<tr>
<td style="text-align: center;">TC-A1</td>
<td style="text-align: center;">新客户识别</td>
<td style="text-align: center;">Hi, we are looking for a contact center solution.</td>
<td style="text-align: center;"><ul>
<li><p>识别为新客户</p></li>
<li><p>触发新客户资料收集流程：Name / Company Name / Email / Phone</p></li>
</ul></td>
<td style="text-align: center;">未进入新客户资料收集流程</td>
</tr>
<tr>
<td style="text-align: center;">TC-A2</td>
<td style="text-align: center;">现有客户识别</td>
<td style="text-align: center;">Our agent cannot receive calls.</td>
<td style="text-align: center;"><ul>
<li><p>识别为现有客户</p></li>
<li><p>触发现有客户资料收集流程：Account ID / Company Name / Agent name / Service number</p></li>
</ul></td>
<td style="text-align: center;">未进入旧客户资料收集流程</td>
</tr>
<tr>
<td style="text-align: center;">TC-A3</td>
<td style="text-align: center;">合作伙伴识别</td>
<td style="text-align: center;">We are a system integrator and want to partner.</td>
<td style="text-align: center;"><ul>
<li><p>识别为合作伙伴</p></li>
<li><p>触发合作伙伴资料收集并转人工：Name / Company Name / Email / Phone</p></li>
</ul></td>
<td style="text-align: center;">未进入新合作伙伴资料收集流程</td>
</tr>
</tbody>
</table>

### B. 产品咨询测试（RAG能力）

<table>
<colgroup>
<col style="width: 10%" />
<col style="width: 13%" />
<col style="width: 21%" />
<col style="width: 39%" />
<col style="width: 14%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: center;"><strong>测试编号</strong></td>
<td style="text-align: center;"><strong>测试名称</strong></td>
<td style="text-align: center;"><strong>输入（例子）</strong></td>
<td style="text-align: center;"><strong>预期行为/结果</strong></td>
<td style="text-align: center;"><strong>失败标准</strong></td>
</tr>
<tr>
<td style="text-align: center;">TC-B1</td>
<td style="text-align: center;">功能咨询</td>
<td style="text-align: center;">Does CINNOX support WhatsApp integration?</td>
<td style="text-align: center;"><ul>
<li><p>正确说明支持，并简要解释功能</p></li>
<li><p>信息来源为官网或用户手册</p></li>
</ul></td>
<td style="text-align: center;">信息错误或无来源</td>
</tr>
<tr>
<td style="text-align: center;">TC-B2</td>
<td style="text-align: center;">使用场景咨询</td>
<td style="text-align: center;">We are a bank. Can you handle high volume inbound calls?</td>
<td style="text-align: center;"><ul>
<li><p>说明支持高并发，并描述ACD、IVR等功能</p></li>
<li><p>不夸大未列功能</p></li>
</ul></td>
<td style="text-align: center;">夸大功能</td>
</tr>
<tr>
<td style="text-align: center;">TC-B3</td>
<td style="text-align: center;">不存在功能测试（幻觉测试）</td>
<td style="text-align: center;">Do you support hologram video calling?</td>
<td style="text-align: center;"><ul>
<li><p>明确说明未支持</p></li>
<li><p>不编造功能</p></li>
<li><p>确定是否转人工咨询</p></li>
</ul></td>
<td style="text-align: center;">编造功能直接Fail</td>
</tr>
</tbody>
</table>

### C. 报价测试（定价准确性）

<table>
<colgroup>
<col style="width: 7%" />
<col style="width: 14%" />
<col style="width: 21%" />
<col style="width: 41%" />
<col style="width: 14%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: center;"><strong>测试编号</strong></td>
<td style="text-align: center;"><strong>测试名称</strong></td>
<td style="text-align: center;"><strong>输入（例子）</strong></td>
<td style="text-align: center;"><strong>预期行为/结果</strong></td>
<td style="text-align: center;"><strong>失败标准</strong></td>
</tr>
<tr>
<td style="text-align: center;">TC-C1</td>
<td style="text-align: center;">国际号码价格查询</td>
<td style="text-align: center;">How much is a US DID number?</td>
<td style="text-align: center;"><ul>
<li><p>调用pricing文档并给出正确价格</p></li>
<li><p>不自创价格</p></li>
</ul></td>
<td style="text-align: center;">价格错误或自创</td>
</tr>
<tr>
<td style="text-align: center;">TC-C2</td>
<td style="text-align: center;">套餐报价</td>
<td style="text-align: center;">What is your pricing for 50 agents?</td>
<td style="text-align: center;"><ul>
<li><p>解释计费方式，如需定制报价转人工</p></li>
<li><p>不胡乱生成总价</p></li>
</ul></td>
<td style="text-align: center;">生成虚假总价</td>
</tr>
<tr>
<td style="text-align: center;">TC-C3</td>
<td style="text-align: center;">汇率错误测试</td>
<td style="text-align: center;">Is the price 5 USD per minute?</td>
<td style="text-align: center;"><ul>
<li><p>根据文档纠正错误</p></li>
<li><p>不迎合错误说法</p></li>
</ul></td>
<td style="text-align: center;">迎合错误价格</td>
</tr>
</tbody>
</table>

### D. 资料收集机制测试

<table>
<colgroup>
<col style="width: 7%" />
<col style="width: 14%" />
<col style="width: 22%" />
<col style="width: 41%" />
<col style="width: 14%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: center;"><strong>测试编号</strong></td>
<td style="text-align: center;"><strong>测试名称</strong></td>
<td style="text-align: center;"><strong>输入（例子）</strong></td>
<td style="text-align: center;"><strong>预期行为/结果</strong></td>
<td style="text-align: center;"><strong>失败标准</strong></td>
</tr>
<tr>
<td style="text-align: center;">TC-D1</td>
<td style="text-align: center;">新客户资料收集完整性</td>
<td style="text-align: center;">I want a demo.</td>
<td style="text-align: center;"><ul>
<li><p>依次收集：Name / Company / Email / Phone</p></li>
</ul></td>
<td style="text-align: center;">少收集字段</td>
</tr>
<tr>
<td style="text-align: center;">TC-D2</td>
<td style="text-align: center;">客户拒绝提供资料</td>
<td style="text-align: center;">I don't want to share my phone number.</td>
<td style="text-align: center;"><ul>
<li><p>说明资料必要性，若拒绝则转人工</p></li>
</ul></td>
<td style="text-align: center;">直接放弃或继续强问</td>
</tr>
</tbody>
</table>

### E. 现有客户问题分流测试

<table>
<colgroup>
<col style="width: 8%" />
<col style="width: 12%" />
<col style="width: 26%" />
<col style="width: 37%" />
<col style="width: 15%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: center;"><strong>测试编号</strong></td>
<td style="text-align: center;"><strong>测试名称</strong></td>
<td style="text-align: center;"><strong>输入（例子）</strong></td>
<td style="text-align: center;"><strong>预期行为/结果</strong></td>
<td style="text-align: center;"><strong>失败标准</strong></td>
</tr>
<tr>
<td style="text-align: center;">TC-E1</td>
<td style="text-align: center;">账单问题</td>
<td style="text-align: center;">I think I was overcharged.</td>
<td style="text-align: center;"><ul>
<li><p>识别为账单问题</p></li>
<li><p>收集账号资料并转人工</p></li>
</ul></td>
<td style="text-align: center;">直接解释账单细节</td>
</tr>
<tr>
<td style="text-align: center;">TC-E2</td>
<td style="text-align: center;">技术故障</td>
<td style="text-align: center;">Voice quality is bad.</td>
<td style="text-align: center;"><ul>
<li><p>识别为技术问题</p></li>
<li><p>收集账号并转人工</p></li>
</ul></td>
<td style="text-align: center;">使用RAG给复杂排查流程</td>
</tr>
</tbody>
</table>

### F. 转人工逻辑测试

<table>
<colgroup>
<col style="width: 8%" />
<col style="width: 13%" />
<col style="width: 25%" />
<col style="width: 36%" />
<col style="width: 15%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: center;"><strong>测试编号</strong></td>
<td style="text-align: center;"><strong>测试名称</strong></td>
<td style="text-align: center;"><strong>输入（例子）</strong></td>
<td style="text-align: center;"><strong>预期行为/结果</strong></td>
<td style="text-align: center;"><strong>失败标准</strong></td>
</tr>
<tr>
<td style="text-align: center;">TC-F1</td>
<td style="text-align: center;">无法解答</td>
<td style="text-align: center;">Explain your database encryption architecture in detail.</td>
<td style="text-align: center;"><ul>
<li><p>不编造不存在的细节</p></li>
<li><p>若知识库无详细内容，有限回答并主动转人工</p></li>
</ul></td>
<td style="text-align: center;">编造功能或技术细节</td>
</tr>
<tr>
<td style="text-align: center;">TC-F2</td>
<td style="text-align: center;">客户强制要求人工</td>
<td style="text-align: center;">I want to talk to a human.</td>
<td style="text-align: center;"><ul>
<li><p>立即转人工</p></li>
<li><p>不再多问</p></li>
</ul></td>
<td style="text-align: center;">继续对话</td>
</tr>
</tbody>
</table>

### G. 连续对话上下文测试

<table>
<colgroup>
<col style="width: 8%" />
<col style="width: 13%" />
<col style="width: 26%" />
<col style="width: 35%" />
<col style="width: 15%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: center;"><strong>测试编号</strong></td>
<td style="text-align: center;"><strong>测试名称</strong></td>
<td style="text-align: center;"><strong>输入（例子）</strong></td>
<td style="text-align: center;"><strong>预期行为/结果</strong></td>
<td style="text-align: center;"><strong>失败标准</strong></td>
</tr>
<tr>
<td style="text-align: center;">TC-G1</td>
<td style="text-align: center;">上下文理解</td>
<td style="text-align: center;"><p>Q1: How much is a UK local number? → 回答后 →</p>
<p>Q2: What about Germany?</p></td>
<td style="text-align: center;"><ul>
<li><p>理解仍在询问DID价格</p></li>
</ul></td>
<td style="text-align: center;">重新解释产品或丢失上下文</td>
</tr>
</tbody>
</table>

### H. 错误容忍测试

<table>
<colgroup>
<col style="width: 8%" />
<col style="width: 13%" />
<col style="width: 26%" />
<col style="width: 35%" />
<col style="width: 15%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: center;"><strong>测试编号</strong></td>
<td style="text-align: center;"><strong>测试名称</strong></td>
<td style="text-align: center;"><strong>输入（例子）</strong></td>
<td style="text-align: center;"><strong>预期行为/结果</strong></td>
<td style="text-align: center;"><strong>失败标准</strong></td>
</tr>
<tr>
<td style="text-align: center;">TC-H1</td>
<td style="text-align: center;">拼写错误</td>
<td style="text-align: center;">Do you have whtsapp intergration?</td>
<td style="text-align: center;"><ul>
<li><p>正确理解为WhatsApp integration</p></li>
</ul></td>
<td style="text-align: center;">无法识别</td>
</tr>
<tr>
<td style="text-align: center;">TC-H2</td>
<td style="text-align: center;">模糊表达</td>
<td style="text-align: center;">I want something for customer service.</td>
<td style="text-align: center;"><ul>
<li><p>主动追问需求</p></li>
</ul></td>
<td style="text-align: center;">直接报价</td>
</tr>
</tbody>
</table>

## 五、失败判定标准

以下任情况视为验收失败：

1.  编造功能

2.  编造价格

3.  无法区分新老客户

4.  未触发资料收集

5.  错误分类问题

6.  未按流程转人工

7.  连续三轮对话逻辑混乱

## 六、数据准确率量化标准

抽样测试 200 个问题：

|              |          |
|:------------:|:--------:|
|   **类型**   | **数量** |
|   产品功能   |    80    |
|     报价     |    40    |
| 现有客户问题 |    40    |
|   混合问题   |    40    |

通过标准：

- 总体准确率 ≥ 95%

- 报价类 100%准确

- 幻觉率 0%

- 客户流程触发正确
