# 海光 DCU 模型优化实践

整理日期：2026-10-06。这里汇总近期在 BW150、BW1100、K100-AI 上的优化工作与实测口径。

## BW150：Qwen3-TTS 的算子与流式流水线

**平台**：单张 BW150 / gfx936，vLLM-Omni 两阶段语音生成流水线。

- 用 hipprof 定位 CodePredictor 的 15 步自回归、小算子与采样开销；通过 HIP 扩展融合 Q/K RMSNorm、RoPE、KV 写入、短序列注意力，以及 Top-K 采样与 embedding 累加。
- 采用静态 KV Cache 和多 batch 桶 GPU Graph，减少重复前缀计算与主机提交开销。
- 对 Code2Wav 使用 BF16、适用条件下的 SDPA 快路径、SplitConv 与细粒度帧长分桶，处理长卷积退化和首包无效 padding。
- 沿参考音频链路继续优化：去掉下游不消费的音频深拷贝、保留 float32 二进制 IPC、减少设备标量同步、限制实际使用的参考码本计算，修复不必要的 CPU 导出。
- 对融合算子、音频协议和码本输出做针对性回归，打包可复现补丁。

**最终合并补丁的新容器验收**：40 并发、400 请求。

| 场景 | Mean RTF | Mean TTFP | 请求结果 |
| :--- | ---: | ---: | :--- |
| 完整 ICL，第二轮 | 0.642658 | 461.080 ms | 400 成功 / 0 失败 |
| xvec，第二轮 | 0.421809 | 244.262 ms | 400 成功 / 0 失败 |

完整 ICL 首轮 RTF 为 0.770327，未达到 0.7 目标。第二轮均值不能代表冷态或 P99 达标。改变参考码本的完整编码器补零图实验未进入默认补丁。

历史组件微测中，batch=40 的 CodePredictor 为 29.187 → 6.785 ms；该数字用于解释组件优化，不与新容器数据拼接为总加速比。

依据：2026-09-29《Qwen3-TTS · BW150 两轮调优复盘》及合并补丁复现记录。

## BW1100：Qwen3.5-9B 的 Decode 热点优化

**平台与负载**：单张 BW1100 / gfx938；SGLang；BF16 权重、FP8 KV、BF16 Mamba state；2K 输入 / 2K 输出，流式、C256、768 请求。

- 将采样惩罚从整词表布尔索引改为融合算子，再对适用请求仅更新少量停止词位置；处理异步快照、过滤、合批与回退语义。
- 根据实际 GDN decode 形状调整分块，并对连续状态递推做数值回归。
- 为单 token 因果卷积增加专用状态更新内核，在寄存器中复用历史值。
- 调整五类线性层的权重物理布局，保留 BF16 权重值，改善后端 GEMM 路径；排除不受益的 LM head 与 embedding。
- 启用镜像已有的 RMSNorm / RoPE / KV 写入融合，配合 NUMA、连接保活与并发筛选完成完整压测。

| 完整测试 | Output throughput | 成功请求 |
| :--- | ---: | :--- |
| 原配置 | 3049.1860 tok/s | 768/768 |
| 最终推荐配置 | 4028.7141 tok/s | 768/768 |

观察提升约 **32.12%**。这是累积配置记录，部分阶段在两张不同物理卡上测量，不是严格逐项消融。C416 的 4067.28 tok/s 不满足吞吐/并发 >10 的条件，最终选择 C256。尚未完成完整模型任务准确率评测与新容器 GPU 吞吐复测。

依据：2026-09-23《Qwen3.5-9B × BW1100：SGLang 调优复盘》。

## K100-AI：Qwen3.8-27B INT8 的短、长上下文优化

**平台与负载**：K100-AI / gfx928；双卡 TP2；SGLang；INT8 W8A8；C8、每轮16请求、输出1024 token。

- 编写 HIP Unified Multi-M LDS GEMV，覆盖 M=1/2/3/4 与四类投影；复用片上激活并缓存权重转置，面向 decode 与 MTP verify 的实际形状优化。
- 用 Triton Long-KV GQA 优化长上下文全注意力路径，并配置 AITER 的真实 GDN 维度。
- 结合 MTP、chunked prefill 与 rocBLAS GEMM 选优，通过实际调用核验确认优化路径生效。
- 修复干净容器中的编译器配置、扩展加载与重复注册问题，将补丁、启动、压测分开交付，完成独立复现。

**2026-10-06 干净容器复现，三轮实测均值**：

| 场景 | Output throughput | TTFT P50 的轮间均值 | TPOT P50 的轮间均值 |
| :--- | ---: | ---: | ---: |
| 4K / 1K | 206.84 tok/s | 3.14 s | 32.62 ms |
| 64K / 1K | 30.39 tok/s | 44.89 s | 184.52 ms |

96/96 请求完成，输出长度均为1024，无请求错误、无乱码替换字符。两次独立容器的64K六轮输出吞吐落在30.26–30.48 tok/s；这类格式与长度检查不替代模型任务准确率评估。

另外一条专项路线覆盖 **W8A8 + DFlash2、TP1 / TP2 / TP4**：长 Agent 上下文验证到约257.9K，优化 prefix/cache resume、all-rank allocator 回收，并修复 TP4 verify 跨 Mamba tracking boundary 时漏 checkpoint 导致的 cached-resume 卡死。该路线与上面的 TP2/MTP 基准分别记录。

依据：《submit1005 交付成果复现验证报告 (Container tuning5)》、K100AI 专项优化 README 与 v1.3.2 release notes。

## 其他模型与系统实践

- **DeepSeek-V4 Flash / BW1100**：单机4P4D分离、Mooncake传输、并发扫描与TTFT/TPOT约束；结合队列和运行日志定位 Prefill 到达率瓶颈。
- **DeepSeek-R1 FP8 / BW1100**：统一客户端评测 vLLM 与 SGLang，在1K/1K、320并发下检查输出吞吐和Mean TPOT，避免前缀缓存污染随机压测。
- **GLM-5.2 FP8 / BW1100**：分析64K/1K下KV容量、Prefill占比和decode调度等待，用SLO筛选可用并发，而非只取最高总吞吐。

## 工作方式

**真实负载 profiling → 形状与热点分析 → 独立数值/状态回归 → 微基准筛选 → 原口径完整压测 → 新容器复现。**

组件耗时、累计GPU内核时长、Output Throughput、Total Throughput与请求延迟分别记录；历史最佳、三轮均值和冷暖状态也分别标注。
