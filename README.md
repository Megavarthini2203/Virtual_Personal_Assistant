# Project Setup and Installation

This repository contains multiple components:
- **WhatsApp Automation (Node.js)**: Uses [whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js) for WhatsApp Web integration and MongoDB for database interactions.
- **PyQt5 GUI Application (Python)**: A desktop application built using PyQt5 and [qfluentwidgets](https://github.com/zserge/qfluentwidgets) for a modern, responsive user interface.
- **AI Model Integration (Python)**: Leverages Hugging Face's Transformers (BERT) and PyTorch for sequence classification, and integrates Google Generative AI functionalities.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Node.js Environment (WhatsApp Automation)](#nodejs-environment-whatsapp-automation)
  - [Python GUI Application](#python-gui-application)
  - [Python AI Model Setup](#python-ai-model-setup)
- [Usage](#usage)
  
---

## Prerequisites

- **Node.js & npm**: Ensure Node.js (v20 or above) and npm are installed.
- **Python**: Python 3.10+ is recommended.
- **MongoDB**: Required for the Node.js component if you plan to use database features.

---

## Installation

### Node.js Environment (WhatsApp Automation)

1. **Navigate to the Node.js project directory:**
   ```bash
   cd Virtual-Personal-Assistant
   ```
  
2. **Install Dependencies:**
This component requires:

- whatsapp-web.js
- qrcode
- mongoose

Install the required packages using:
bash
```
npm install whatsapp-web.js qrcode mongoose
```

3. **Configuration & Running:**
Ensure you have your MongoDB connection details configured if you intend to use database features.
Start your application with:
bash
```
node test.js
```

4. **Install Python Dependencies:**
   
This module uses:
- PyQt5 for the GUI framework.
- qfluentwidgets for enhanced widget styling and theming.

Install them using pip:
bash
```
pip install PyQt5
pip install "PyQt-Fluent-Widgets[full]" -i https://pypi.org/simple/
```

5. **Other Dependencies:**
   
This part of the project utilizes:

- transformers for BERT model implementations.
- torch for deep learning.
- google-generativeai for accessing Google Generative AI functionalities.

Install the required packages using:
bash
```
pip install transformers torch google-generativeai
```

6. **Download model from my kaggle account:**

[KAGGLE LINK]

Place the `model` and `tokenizer` folder inside the `brain`

![image](https://github.com/user-attachments/assets/b65b011a-7eec-4690-bc4b-0a0e578fd256)

