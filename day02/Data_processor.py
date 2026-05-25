from loguru import logger
import csv

class DataProcessor:
    def __init__(self,filename):
        self.filename=filename
        self.data=[]
        logger.info(f"data processor created for {filename}")

    def read(self):
        try:
            with open(self.filename,"r") as f:
                reader = csv.DictReader(f)
                self.data=list(reader)
                logger.info(f"Read {len(self.data)} rows")    
        except FileNotFoundError:
            logger.error(f"file {filename} not found")
    def clean(self):
        cleaned = []
        for row in self.data:
            if row["salary"] == "":
                logger.warning(f"Skipping {row['name']} - missing salary")
                continue
            if int(row["age"]) <= 0:
                logger.warning(f"Skipping {row['name']} - invalid age")
                continue
            cleaned.append(row)
        self.data = cleaned
        logger.info(f"{len(self.data)} rows after cleaning")

    def save(self, output_file):
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["name","age","salary","city"])
            writer.writeheader()
            writer.writerows(self.data)
            logger.info(f"Saved clean data to {output_file}")
processor = DataProcessor("day02/data.csv")
processor.read()
processor.clean()
processor.save("day02/clean_data.csv")
