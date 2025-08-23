#!/bin/bash

# Sync project agents with agent reserves
# This script updates all project agents to match the latest versions in agent-reserves

RESERVES_DIR="/home/jsnitsel/.claude/agent-reserves"
PROJECTS_DIR="/home/jsnitsel/devel"

echo "Syncing project agents with agent reserves..."
echo "========================================"

# Find all projects with .claude/agents directories
for project_path in "$PROJECTS_DIR"/*; do
    if [ -d "$project_path" ]; then
        project_name=$(basename "$project_path")
        agents_dir="$project_path/.claude/agents"
        
        if [ -d "$agents_dir" ]; then
            echo
            echo "Processing project: $project_name"
            echo "Agents directory: $agents_dir"
            
            # List current agents in project
            current_agents=$(ls "$agents_dir"/*.md 2>/dev/null | xargs -n1 basename 2>/dev/null || true)
            
            if [ -n "$current_agents" ]; then
                echo "Current agents: $(echo $current_agents | tr '\n' ' ')"
                
                # Copy each agent from reserves if it exists
                for agent_file in $current_agents; do
                    reserve_file="$RESERVES_DIR/$agent_file"
                    project_file="$agents_dir/$agent_file"
                    
                    if [ -f "$reserve_file" ]; then
                        if ! diff -q "$reserve_file" "$project_file" >/dev/null 2>&1; then
                            echo "  Updating: $agent_file"
                            cp "$reserve_file" "$project_file"
                        else
                            echo "  Up to date: $agent_file"
                        fi
                    else
                        echo "  WARNING: $agent_file not found in reserves"
                    fi
                done
            else
                echo "No agents found in project"
            fi
        else
            echo "Project $project_name: No .claude/agents directory"
        fi
    fi
done

echo
echo "Sync complete!"