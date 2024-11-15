import os
import re
import uuid

def generate_trace_id():
    """Generate a unique UUID for banyancloud_trace_id."""
    return str(uuid.uuid4())

def merge_tags(existing_tags, trace_id):
    """Merge existing tags with banyancloud_trace_id, ensuring no duplicates."""
    # Check if banyancloud_trace_id already exists in the existing tags
    if 'banyancloud_trace_id' in existing_tags:
        return existing_tags  # Return existing tags if banyancloud_trace_id already exists
    # Add banyancloud_trace_id to existing tags if not already present
    return f"merge({existing_tags.strip()}, {{ banyancloud_trace_id = \"{trace_id}\" }})"

def add_trace_id_to_resource(content):
    """Add banyancloud_trace_id to each resource's tags in the given Terraform file content."""
    updated_content = ""
    resource_block_pattern = re.compile(r'(resource\s+\"[^\"]+\"\s+\"[^\"]+\"\s*{[^}]*})', re.DOTALL)
    tags_pattern = re.compile(r'tags\s*=\s*\{[^}]*\}', re.DOTALL)
    
    position = 0
    for match in resource_block_pattern.finditer(content):
        resource_block = match.group(0)
        trace_id = generate_trace_id()  # Generate unique trace_id for each resource
        tag_match = tags_pattern.search(resource_block)

        if tag_match:
            # Tags block exists; wrap it in a merge function with banyancloud_trace_id
            existing_tags = tag_match.group(0).split('=', 1)[1].strip()  # Get the existing tags block
            updated_tags = merge_tags(existing_tags, trace_id)
            updated_resource_block = resource_block.replace(tag_match.group(0), f"tags = {updated_tags}", 1)
        else:
            # No tags block; add a new one immediately after the opening brace
            updated_resource_block = resource_block.replace(
                '{', f'{{\n  tags = {{\n    banyancloud_trace_id = \"{trace_id}\"\n  }}\n', 1
            )
        
        updated_content += content[position:match.start()] + updated_resource_block
        position = match.end()
    
    updated_content += content[position:]
    return updated_content

def process_tf_files_in_directory(directory):
    """Process all .tf files in the given directory, adding banyancloud_trace_id to resources."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".tf"):
                file_path = os.path.join(root, file)
                
                with open(file_path, 'r') as f:
                    content = f.read()
                
                updated_content = add_trace_id_to_resource(content)
                
                with open(file_path, 'w') as f:
                    f.write(updated_content)
                print(f"Updated file: {file_path}")

if __name__ == '__main__':
    directory = os.getenv('INPUT_DIRECTORY', '.')  # Default to current directory
    process_tf_files_in_directory(directory)
