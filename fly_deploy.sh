flyctl apps create --name my_app

python set_fly_secrets.py

flyctl machine run . --schedule daily --memory 1024
# flyctl machine run . --schedule hourly --memory 1024
# if error: 
# flyctl machine run . --schedule daily --memory 1024 --wg=false


# Add command to destroy/remove machines
echo "To destroy all machines: flyctl machine destroy"
echo "To destroy a specific machine: flyctl machine destroy <machine-id>"

# Add SSH access commands
echo "To list all machines: flyctl machine list"
echo "To SSH into a machine: flyctl ssh console -s <machine-id>"

# Add these commands to view logs
echo "To view all logs: flyctl logs"

# Add command to destroy/remove the entire app
echo "To destroy the entire app: flyctl apps destroy ui-grounding-annotator"
