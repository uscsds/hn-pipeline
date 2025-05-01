#!/bin/bash
echo "🗜️ Zipping fetch lambda function..."
cd ../terraform/fetch_hn_data
zip -r lambda.zip .
echo "🗜️ Zipping clean lambda function..."
cd ../clean_hn_data
zip -r lambda.zip .
echo "🗜️ Zipping process lambda function..."
cd ../process_hn_data
zip -r lambda.zip .

cd ../
