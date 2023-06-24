scp -i $1 ubuntu@$2:~/Cameraman/image_output.zip ~/Desktop/

timestamp=$(date +%Y%m%d%H%M%S)
unzip_dir="$HOME/Desktop/image_output_$timestamp"

# Unzip the archive
unzip ~/Desktop/image_output.zip -d "$unzip_dir"