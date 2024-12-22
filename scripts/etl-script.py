import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Load static airport data
airport_dim = glueContext.create_dynamic_frame.from_catalog(database="airline-db", table_name="airport_data")

# Load dynamic flight data
flight_raw = glueContext.create_dynamic_frame.from_catalog(database="airline-db", table_name="flight_data")

# Join flight data with airport data for OriginAirportID
flight_with_origin = Join.apply(
    frame1=flight_raw, 
    frame2=airport_dim, 
    keys1=["originairportid"], 
    keys2=["airport_id"]
).rename_field("city", "origincity").rename_field("state", "originstate")

# Join again for DestAirportID
flight_enriched = Join.apply(
    frame1=flight_with_origin, 
    frame2=airport_dim, 
    keys1=["destairportid"], 
    keys2=["airport_id"]
).rename_field("city", "destcity").rename_field("state", "deststate")

# Select required columns
flight_final = flight_enriched.select_fields([
    "carrier", 
    "originairportid", 
    "destairportid", 
    "origincity", 
    "originstate", 
    "destcity", 
    "deststate", 
    "depdelay", 
    "arrdelay"
])

# Write to Redshift
glueContext.write_dynamic_frame.from_options(
    frame=flight_final,
    connection_type="redshift",
    connection_options={
        "dbtable": "flight_fact",
        "database": "airline_db",
        "aws_iam_role": "arn:aws:iam::123456789012:role/GlueServiceRole"
    }
)

job.commit()
