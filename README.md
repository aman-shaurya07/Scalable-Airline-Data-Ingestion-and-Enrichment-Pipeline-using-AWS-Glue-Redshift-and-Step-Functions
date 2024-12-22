# Scalable Airline Data Ingestion and Enrichment Pipeline using AWS Glue, Redshift, and Step Functions

This project demonstrates an end-to-end data pipeline for processing and enriching daily flight data using AWS services. The pipeline integrates static airport information with dynamic flight data and loads enriched data into Amazon Redshift for analysis. The project is implemented using AWS CLI for resource creation and management.

## Project Overview

### **Objective**
To build a scalable data pipeline that:
- Processes daily flight data dynamically uploaded to Amazon S3.
- Enriches flight data with static airport information (city, state).
- Stores enriched data in Amazon Redshift for analytics.

### **Tech Stack**
1. **AWS S3**: For storing raw flight and airport data.
2. **AWS Glue**: For schema detection (Crawler) and ETL processing.
3. **Amazon Redshift**: Data warehouse to store processed data.
4. **AWS Step Functions**: To orchestrate the data pipeline.
5. **AWS CloudTrail + EventBridge**: To monitor file uploads and trigger the pipeline.
6. **AWS SNS**: For pipeline success/failure notifications.

### **Data Sources**
- **Airport Data (Static)**: `airport_codes.csv`
  - Contains airport IDs, city, state, and airport names.
- **Flight Data (Dynamic)**: `flights.csv`
  - Contains carrier information, origin/destination airport IDs, and delays.

## File Structure

```
airline-data-ingestion-project/
├── data/
│   ├── airport_codes.csv          # Static airport data
│   ├── sample_flights.csv         # Initial sample flight data
│   └── new_flights.csv            # Example of new flight data
├── scripts/
│   ├── etl-script.py              # Glue ETL job script
│   ├── create_resources.sh        # Script to create AWS resources
│   ├── delete_resources.sh        # Script to clean up AWS resources
│   ├── step_function_definition.json # Step Function workflow definition
│   ├── glue_trust_policy.json     # Glue service role trust policy
│   └── example_queries.sql        # Redshift queries for verification
└── README.md                      # Project documentation
```

## Pipeline Flow

1. **S3 File Upload**:
   - `flights.csv` is uploaded to an S3 bucket.
   - `airport_codes.csv` is uploaded once as static data.

2. **CloudTrail + EventBridge**:
   - Monitors S3 for new file uploads and triggers the Step Functions workflow.

3. **Step Functions Workflow**:
   - Runs the Glue Crawler to detect and catalog the schema of new files.
   - Executes the Glue ETL job to enrich and process flight data.

4. **Glue ETL**:
   - Joins flight data with airport information.
   - Outputs enriched data to Amazon Redshift.

5. **Amazon Redshift**:
   - Stores enriched data in the `flight_fact` table.

6. **SNS Notifications**:
   - Sends success/failure notifications at the end of the workflow.

## Step-by-Step Implementation

### **1. Data Preparation**
- Place `airport_codes.csv` and `sample_flights.csv` in the `data/` folder.

### **2. Resource Creation**
Run the following script to create all AWS resources:
```bash
bash scripts/create_resources.sh
```
This script will:
- Create an S3 bucket and upload data.
- Create Glue Crawlers for schema detection.
- Deploy the Step Functions workflow.

### **3. Glue ETL Job**
- The ETL script (`scripts/etl-script.py`) will:
  - Extract flight and airport data from S3.
  - Enrich flight data with city/state information from airport data.
  - Load enriched data into the `flight_fact` table in Redshift.

### **4. Testing the Pipeline**
- Simulate new data by uploading `new_flights.csv` to the S3 bucket:
```bash
aws s3 cp data/new_flights.csv s3://<your-bucket-name>/daily-flight-data/
```
- Verify execution in Step Functions:
```bash
aws stepfunctions list-executions --state-machine-arn <StepFunctionArn>
```

### **5. Querying Data in Redshift**
Use the example queries in `scripts/example_queries.sql` to validate the data:
```sql
-- View enriched flight data
SELECT * FROM flight_fact LIMIT 10;

-- Check total rows
SELECT COUNT(*) FROM flight_fact;
```

### **6. Resource Cleanup**
Run the following script to delete all resources:
```bash
bash scripts/delete_resources.sh
```

## Sample Data

### **Airport Data** (`airport_codes.csv`):
```csv
airport_id,city,state,name
10165,Adak Island,AK,Adak
10299,Anchorage,AK,Ted Stevens Anchorage International
10304,Aniak,AK,Aniak Airport
```

### **Flight Data** (`sample_flights.csv`):
```csv
Carrier,OriginAirportID,DestAirportID,DepDelay,ArrDelay
DL,11433,13303,-3,1
DL,14869,12478,0,-8
DL,14057,14869,-4,-15
```

## AWS CLI Commands

### **1. S3 Commands**
```bash
# Create bucket
aws s3api create-bucket --bucket airline-data-ingestion --region us-east-1

# Upload files
aws s3 cp data/airport_codes.csv s3://airline-data-ingestion/dimensional-data/
aws s3 cp data/sample_flights.csv s3://airline-data-ingestion/daily-flight-data/
```

### **2. Glue Commands**
```bash
# Create Crawlers
aws glue create-crawler --name airport-crawler --role GlueServiceRole --database-name airline-db \
  --targets '{"S3Targets": [{"Path": "s3://airline-data-ingestion/dimensional-data/"}]}'

aws glue create-crawler --name flight-crawler --role GlueServiceRole --database-name airline-db \
  --targets '{"S3Targets": [{"Path": "s3://airline-data-ingestion/daily-flight-data/"}]}'

# Start Crawlers
aws glue start-crawler --name airport-crawler
aws glue start-crawler --name flight-crawler
```

### **3. Redshift Commands**
```sql
CREATE TABLE flight_fact (
    carrier VARCHAR(5),
    origin_airport_id INT,
    dest_airport_id INT,
    origin_city VARCHAR(50),
    origin_state VARCHAR(2),
    dest_city VARCHAR(50),
    dest_state VARCHAR(2),
    dep_delay INT,
    arr_delay INT
);
```

### **4. Step Functions Commands**
```bash
# Create State Machine
aws stepfunctions create-state-machine --name AirlineDataPipeline --role-arn <StepFunctionRoleArn> \
  --definition file://scripts/step_function_definition.json

# Start Execution
aws stepfunctions start-execution --state-machine-arn <StepFunctionArn>
```

## Notes
- Replace placeholders (e.g., `<StepFunctionArn>`, `<your-bucket-name>`) with actual values.
- Ensure appropriate IAM roles and permissions are configured.

## Future Enhancements
- Add monitoring using AWS CloudWatch.
- Implement error handling in the ETL script.
- Optimize Redshift queries for performance.

## License
This project is licensed under the MIT License.

