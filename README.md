# Educational Web Scraper

This project is an educational tool to demonstrate how to use Python libraries like Selenium, MongoDB, and Schedule for web scraping. The scraper collects publicly available job data from a specified website and stores it in MongoDB.

---

## **Key Features**

- Uses **Selenium** for browser automation and web interaction.
- Includes proxy support for enhanced anonymity.
- Saves scraped data in **MongoDB**.
- Allows scheduling of scraping tasks using the **schedule** library.
- Checks the `robots.txt` file of the target website for scraping permissions.
- Logs all activities and errors in `webscraper.log`.

---

## **Important Notes**

### **Data Privacy and Legal Compliance**
1. **Respect `robots.txt`:** This scraper checks the `robots.txt` file of the target website before scraping. If scraping is disallowed, the scraper will log a warning and terminate.
2. **Terms of Service:** Always adhere to the terms of service of the target website. Unauthorized scraping may violate these terms.
3. **No Personal Data:** This scraper does not target or process personal data.
4. **Commercial Use:** This project is for educational purposes only. Do not use it for commercial purposes without explicit consent from the website owner.

### **What is `robots.txt`?**
`robots.txt` is a file used by websites to communicate with web crawlers. It specifies which parts of the website are allowed or disallowed for automated access. Learn more at [robotstxt.org](https://www.robotstxt.org/).

---

## **Requirements**

- **Python**: Version 3.8 or higher
- **Browser**: Google Chrome
- **Database**: MongoDB (local or remote instance)

### **Dependencies**
All required Python libraries are listed in `requirements.txt`. Install them using:
```bash
pip install -r requirements.txt
