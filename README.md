<p align="center">
  <img src="https://raw.githubusercontent.com/gugugu-b/gugugu-b/main/assets/cluster-banner.gif" width="100%" alt="Pionites — BW150, BW1100 and K100-AI model optimization. Animated HIP / Triton / LLM / TTS pipeline and profiling terminal." />
</p>

<p align="center">
  <strong>Hygon DCU Model Optimization · HIP / Triton Kernels · AI Infrastructure</strong><br />
  BW150 · BW1100 · K100-AI ｜ 从算子热点到端到端推理性能。
</p>

<p align="center">
  <a href="mailto:zhangzixuan761@gmail.com"><img src="https://img.shields.io/badge/Email-zhangzixuan761%40gmail.com-38BDF8?style=flat-square&logo=gmail&logoColor=white" alt="Email" /></a>
  <img src="https://img.shields.io/badge/Location-Hangzhou-94A3B8?style=flat-square" alt="Based in Hangzhou" />
  <a href="https://github.com/gugugu-b?tab=repositories"><img src="https://img.shields.io/badge/Explore-My_Repos-2DD4BF?style=flat-square&logo=github&logoColor=white" alt="Explore my repositories" /></a>
</p>

## 👋 关于我

Hi, I'm **Pionites** — 专注 **国产 GPU / DCU 模型性能优化与 AI 基础设施**。

近期重点在海光 **BW150、BW1100、K100-AI** 上做模型优化：从真实调用的 profiling 出发，编写 HIP / Triton 专用算子，优化数据布局、GPU Graph 与服务流水线，再用数值回归和完整压测验证收益。

- **模型与算子**：Qwen TTS / LLM、INT8 W8A8、GEMM / GEMV、Attention、GDN、采样与卷积。
- **性能工程**：hipprof、算子微基准、TTFT / TPOT / RTF、跨容器复现与补丁交付。
- **分布式通信**：NCCL / RCCL，GPUDirect RDMA，通信日志分析与瓶颈定位。
- **训练与推理**：国产 GPU / DCU 软件栈，vLLM 压测，基于 TTFT / TPOT 的 SLO 评估。

## 🔥 近期重点：海光 DCU 模型优化

| 平台 / 模型 | 主要工作 | 实测记录 |
| :--- | :--- | :--- |
| **BW150 · Qwen3-TTS-12Hz-1.7B** | HIP 融合注意力与采样；静态 KV Cache、多 batch GPU Graph；Code2Wav BF16 / SDPA / SplitConv；参考音频 IPC 与同步优化 | 单卡、40 并发、400 请求，新容器完整 ICL **第二轮 Mean RTF 0.643 / TTFP 461 ms**，400/400 成功 |
| **BW1100 · Qwen3.5-9B** | 稀疏采样惩罚、GDN 分块、因果卷积状态更新、BF16 权重物理布局与融合路径 | 单卡 BF16、2K/2K、C256：输出吞吐 **3049 → 4029 tok/s（观察提升 32.1%）**，768/768 成功 |
| **K100-AI · Qwen3.8-27B INT8** | HIP Multi-M LDS GEMV、Triton Long-KV GQA、AITER 形状配置、MTP 与 rocBLAS GEMM 选优 | TP2、C8，干净容器三轮均值：**4K/1K 206.84 tok/s；64K/1K 30.39 tok/s**，96/96 请求通过长度与错误检查 |

> 以上均为各自测试条件下的记录。BW150 的 ICL 首轮 RTF 为 0.770；BW1100 部分阶段使用不同物理卡，32.1% 为累积配置观察结果。各场景的吞吐、组件微测与端到端延迟分别统计。

**更多实践**：DeepSeek 的 Prefill / Decode 分离与高并发评测、GLM 长上下文 SLO 分析，以及 K100-AI 上 TP1 / TP2 / TP4 的 Agent 长上下文、缓存恢复和稳定性优化。

📖 [模型优化案例与测试口径](docs/model-optimization.md)

`Profiling → Kernel / Layout / Pipeline → Numerical Regression → End-to-End Benchmark → Reproduction`

<p align="center">
  <img src="https://raw.githubusercontent.com/gugugu-b/gugugu-b/main/assets/operator-hotspots.gif" width="100%" alt="BW1100 Qwen3.5-9B baseline profiling: animated scan of fixed GPU kernel time shares. GEMM 41.6%, GDN 15.6%, nonzero 12.4%." />
</p>

算子热点来自 BW1100 / Qwen3.5-9B 基线的 15 个 decode 步采样，展示累计 GPU 内核时长占比。[采样口径与优化案例](docs/model-optimization.md)

## ⚙️ 技术地图

| 方向 | 技术与关注点 |
| :--- | :--- |
| **算子开发** | HIP C++ · Triton · GEMM / GEMV · GQA · GDN · Top-K / Sampling · 因果卷积 |
| **模型优化** | BW150 / gfx936 · BW1100 / gfx938 · K100-AI / gfx928 · INT8 W8A8 · BF16 · GPU Graph |
| **分析与验收** | DTK hipprof · rocBLAS / MIOpen · 数值回归 · 算子微测 · 跨容器复现 |
| **网络与互联** | RDMA · RoCEv2 · InfiniBand · Spine-Leaf · Dragonfly |
| **通信与并行** | NCCL / RCCL · Ring / Tree · Channel / QP · DP / TP / PP · MoE alltoallv |
| **性能诊断** | ECN / PFC / DCQCN · GDR · Buffer / Tail Latency · 通信日志与监控指标 |
| **训练与推理** | DCU / 国产 GPU · vLLM / vLLM-Omni · SGLang · DeepEP · MTP / DFlash · 吞吐与延迟压测 |
| **调度与运维** | Kubernetes · NUMA Affinity · Slurm · 服务器部署与监控 |

## 🚀 我的项目

### 推理压测与性能调优

| 项目 | 用途 |
| :--- | :--- |
| [**SLO**](https://github.com/gugugu-b/SLO) | 给定 TTFT / TPOT 阈值，自适应搜索 vLLM 的临界最大并发数。 |
| [**bench**](https://github.com/gugugu-b/bench) | 扫描固定并发点，建立 vLLM 的吞吐与延迟表现。 |
| [**dcu-train-cookbook**](https://github.com/gugugu-b/dcu-train-cookbook) | DCU 训练性能参数与调优 cookbook。 |
| [**rccl-study-notes**](https://github.com/gugugu-b/rccl-study-notes) | RCCL 学习笔记：7 天学习路径与性能调优。 |

### 硬件与运维笔记

| 项目 | 用途 |
| :--- | :--- |
| [**server-testing-lab**](https://github.com/gugugu-b/server-testing-lab) | 服务器运维学习笔记：部署、配置、监控与安全实践。 |
| [**nas-resources-storage**](https://github.com/gugugu-b/nas-resources-storage) | NAS 硬件测试文档与资源：电源、SSD、固件与系统配置。 |

<details>
<summary><strong>📚 学习资源与 Fork 项目</strong></summary>

这些仓库 Fork 自其他开源项目，方便学习与探索；原作者与上游信息见各仓库。

| 仓库 | 内容 |
| :--- | :--- |
| [AIInfra](https://github.com/gugugu-b/AIInfra) | 从芯片与硬件到大模型训练、推理软件栈的 AI 基础设施资源。 |
| [open-rdma](https://github.com/gugugu-b/open-rdma) | open-rdma 项目介绍与上手指南。 |
| [CS-Books](https://github.com/gugugu-b/CS-Books) | 计算机经典书籍、学习笔记与面试资料。 |
| [HermesPet](https://github.com/gugugu-b/HermesPet) | 住在 MacBook 刘海里的桌面 AI 伴侣，使用 Swift / SwiftUI。 |

</details>

## ✨ 持续构建

<p align="center">
  <a href="https://github.com/gugugu-b?tab=overview"><img src="https://raw.githubusercontent.com/gugugu-b/gugugu-b/main/assets/contribution-heatmap.gif" width="100%" alt="Animated heatmap of my real GitHub contributions over the past year. The date range is shown in the image." /></a>
</p>

热力图使用 GitHub 实际贡献记录，快照日期见图中时间范围；扫描光效展示时间轴。

---

<p align="center">
  <strong>Build · Measure · Tune · Repeat</strong><br />
  欢迎交流 DCU 模型优化、HIP / Triton 算子、分布式通信与推理性能。<br />
  <a href="mailto:zhangzixuan761@gmail.com">zhangzixuan761@gmail.com</a>
</p>
