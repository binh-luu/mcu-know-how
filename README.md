# MCU Knowledge Base

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![STMicroelectronics](https://img.shields.io/badge/MCU-STM32F407G--DISC1-blue)](https://www.st.com/en/evaluation-tools/stm32f4discovery.html)
[![Infineon](https://img.shields.io/badge/MCU-KIT--T2G--B--H--LITE-green)](https://www.infineon.com/traveo2)

## Overview

This repository provides a **knowledge base** for learning and developing with **microcontroller units (MCUs)** using two popular hardware platforms:

- **STMicroelectronics STM32F407G-DISC1**
- **Infineon KIT-T2G-B-H-LITE**

The document covers:
- Hardware kit overviews  
- Required software tools and environments  
- Reference documentation and resources  

It serves as a quick-start guide for developers, students, and engineers working on embedded systems, automotive, or industrial applications.

---

## Table of Contents

- [Overview](#overview)
- [Hardware Kits](#hardware-kits)
  - [STM32F407G-DISC1](#stm32f407g-disc1)
  - [KIT-T2G-B-H-LITE](#kit-t2g-b-h-lite)
- [Software Tools](#software-tools)
  - [STM32F407G-DISC1 Tools](#stm32f407g-disc1-tools)
  - [KIT-T2G-B-H-LITE Tools](#kit-t2g-b-h-lite-tools)
- [Technical Resources](#technical-resources)
- [License](#license)

---

## Hardware Kits

### STM32F407G-DISC1

The **STM32F407G-DISC1** (Discovery Kit) is a development board based on the **STM32F407VGT6** microcontroller featuring an ARM® Cortex®-M4 core running at 168 MHz.

**Key Features**
- MCU: STM32F407VGT6 (ARM Cortex-M4, 1 MB Flash, 192 KB RAM)  
- On-board **ST-LINK/V2** debugger and programmer  
- Integrated peripherals: accelerometer, audio DAC, microphone, LEDs, pushbuttons  
- USB OTG micro-AB connector  
- Expansion headers for external modules  

**Typical Applications**
- Embedded systems prototyping  
- Sensor interfacing and control  
- Real-time processing and DSP applications  

**Product Page:** [ST STM32F407G-DISC1](https://www.st.com/en/evaluation-tools/stm32f4discovery.html)

---

### KIT-T2G-B-H-LITE

The **KIT-T2G-B-H-LITE** is a cost-effective evaluation board for the **Infineon Traveo™ II Body High** MCU family, designed for automotive and industrial applications.

**Key Features**
- MCU: Traveo™ II (Arm® Cortex®-M4/M0+)  
- Flash and SRAM suitable for advanced automotive systems  
- On-board DAPLink programmer/debugger  
- Communication interfaces: CAN FD, LIN, SPI, UART, I²C  
- Integrated power supply and expansion headers  

**Typical Applications**
- Automotive body electronics (lighting, HVAC, seat control)  
- Industrial control and communication systems  
- Evaluation of Traveo II software drivers and APIs  

**Product Page:** [Infineon KIT-T2G-B-H-LITE](https://www.infineon.com/traveo2)

---

## Software Tools

### STM32F407G-DISC1 Tools

| Tool | Description | Download |
|------|--------------|-----------|
| **STM32CubeIDE** | Integrated development environment for coding, compiling, and debugging STM32 MCUs | [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html) |
| **STM32CubeMX** | MCU and peripheral configuration tool with HAL code generation | [STM32CubeMX](https://www.st.com/en/development-tools/stm32cubemx.html) |
| **ST-LINK Utility / STM32CubeProgrammer** | Flashing and debugging interface for ST-LINK | [CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html) |
| **FreeRTOS / CMSIS** | Optional RTOS and low-level abstraction layer | [CMSIS](https://arm-software.github.io/CMSIS_5/) |

**Alternative IDEs**
- Keil µVision (ARM MDK)
- IAR Embedded Workbench for ARM

---

### KIT-T2G-B-H-LITE Tools

| Tool | Description | Download |
|------|--------------|-----------|
| **ModusToolbox™ IDE** | Unified development platform for Traveo II and PSoC MCUs | [ModusToolbox](https://www.infineon.com/modustoolbox) |
| **Device Configurator** | Pin, clock, and peripheral configuration tool | Included in ModusToolbox |
| **Peripheral Driver Library (PDL)** | Low-level APIs for Traveo II MCU peripherals | [Infineon PDL](https://www.infineon.com/pdl) |
| **DAPLink / J-Link Debugger** | Debugging and programming interfaces | [Segger J-Link](https://www.segger.com/products/debug-probes/j-link/) |

**Additional Tools**
- AutoSAR-compatible software components (for automotive applications)

---

## Technical Resources

### STM32F407G-DISC1
- [STM32F407G-DISC1 Product Page](https://www.st.com/en/evaluation-tools/stm32f4discovery.html)  
- [STM32F407VGT6 Datasheet](https://www.st.com/resource/en/datasheet/stm32f407vg.pdf)  
- [STM32F4 Reference Manual (RM0090)](https://www.st.com/resource/en/reference_manual/dm00031020.pdf)  
- [STM32CubeF4 Firmware Package](https://www.st.com/en/embedded-software/stm32cubef4.html)

### KIT-T2G-B-H-LITE
- [KIT-T2G-B-H-LITE Product Page](https://www.infineon.com/traveo2)  
- [Traveo II Family Overview](https://www.infineon.com/traveo2)  
- [ModusToolbox Software Portal](https://www.infineon.com/modustoolbox)  
- [Traveo II Reference Manual & Application Notes](https://www.infineon.com/cms/en/design-support/tools/)  

---

## License

This repository is licensed under the [MIT License](LICENSE).

---

© 2025 — for educational and reference use.
