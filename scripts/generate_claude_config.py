#!/usr/bin/env python3
"""
Claude Desktop Config Generator

Cross-platform script to generate claude_desktop_config.json with absolute paths
to MCP servers and integrate with Claude Desktop.

Supports Windows, macOS, and Linux.
"""

import json
import os
import platform
import shutil
from pathlib import Path
from typing import Dict, Any, Optional


class ClaudeConfigGenerator:
    """Generates and installs Claude Desktop configuration."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize with project root directory."""
        self.project_root = project_root or Path(__file__).parent.parent
        self.system = platform.system().lower()
        
    def get_claude_config_path(self) -> Path:
        """Get Claude Desktop config path for current platform."""
        home = Path.home()
        
        if self.system == "windows":
            # Windows: %APPDATA%\Claude\claude_desktop_config.json
            return home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
        elif self.system == "darwin":  # macOS
            # macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
            return home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        else:  # Linux
            # Linux: ~/.config/claude_desktop_config.json
            return home / ".config" / "claude_desktop_config.json"
    
    def find_mcp_servers(self) -> Dict[str, Dict[str, Any]]:
        """Find all MCP servers and their entry points."""
        servers = {}
        servers_dir = self.project_root / "servers"
        
        if not servers_dir.exists():
            raise FileNotFoundError(f"Servers directory not found: {servers_dir}")
        
        for server_dir in servers_dir.iterdir():
            if not server_dir.is_dir() or server_dir.name.startswith("_"):
                continue
                
            # Look for different server entry points
            entry_points = [
                Path("run_server.py"),  # web_search, page_analyzer
                Path("src") / server_dir.name / "server.py",  # query_generator
            ]
            
            for entry_point in entry_points:
                if (server_dir / entry_point).exists():
                    server_name = server_dir.name
                    if server_name == "web_search":
                        server_name = "web_search"
                    elif server_name == "page_analyzer":
                        server_name = "page_analyzer"
                    elif server_name == "query_generator":
                        server_name = "query_generator"
                    
                    servers[server_name] = {
                        "command": "uv",
                        "args": [
                            "--directory",
                            # str(entry_point.absolute()),
                            str(server_dir),
                            "run",
                            "python",
                            str(entry_point)
                        ]
                    }
                    break
        
        return servers
    
    def generate_config(self) -> Dict[str, Any]:
        """Generate Claude Desktop configuration."""
        servers = self.find_mcp_servers()
        
        if not servers:
            raise RuntimeError("No MCP servers found")
        
        config = {
            "mcpServers": servers
        }
        
        return config
    
    def save_config(self, config: Dict[str, Any], output_path: Optional[Path] = None) -> Path:
        """Save configuration to file."""
        if output_path is None:
            output_path = self.project_root / ".claude" / "claude_desktop_config.json"
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def install_config(self, backup: bool = True) -> bool:
        """Install configuration to Claude Desktop."""
        try:
            claude_config_path = self.get_claude_config_path()
            local_config_path = self.project_root / "configs" / "claude_desktop_config.json"
            
            if not local_config_path.exists():
                raise FileNotFoundError(f"Local config not found: {local_config_path}")
            
            # Create Claude config directory if it doesn't exist
            claude_config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Backup existing config
            if backup and claude_config_path.exists():
                backup_path = claude_config_path.with_suffix('.json.backup')
                shutil.copy2(claude_config_path, backup_path)
                print(f"✅ Backed up existing config to: {backup_path}")
            
            # Copy new config
            shutil.copy2(local_config_path, claude_config_path)
            print(f"✅ Installed config to: {claude_config_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to install config: {e}")
            return False
    
    # TODO: adjust finding logic
    def validate_servers(self) -> bool:
        """Validate that all server entry points exist and are executable."""
        try:
            servers = self.find_mcp_servers()
            print(f"Found {len(servers)} MCP servers:")
            
            all_valid = True
            for name, config in servers.items():
                entry_point = Path(config["args"][0])
                if entry_point.exists():
                    print(f"  ✅ {name}: {entry_point}")
                else:
                    print(f"  ❌ {name}: {entry_point} (NOT FOUND)")
                    all_valid = False
            
            return all_valid
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Claude Desktop configuration")
    parser.add_argument("--install", action="store_true", 
                       help="Install config to Claude Desktop")
    parser.add_argument("--no-backup", action="store_true",
                       help="Don't backup existing config when installing")
    parser.add_argument("--validate", action="store_true",
                       help="Validate server paths only")
    parser.add_argument("--output", type=Path,
                       help="Output path for config file")
    
    args = parser.parse_args()
    
    try:
        generator = ClaudeConfigGenerator()
        
        # Validation mode
        if args.validate:
            print("🔍 Validating MCP servers...")
            if generator.validate_servers():
                print("✅ All servers validated successfully")
                return 0
            else:
                print("❌ Some servers failed validation")
                return 1
        
        # Generate configuration
        print("🔧 Generating Claude Desktop configuration...")
        config = generator.generate_config()
        
        # Save configuration
        output_path = generator.save_config(config, args.output)
        print(f"✅ Configuration saved to: {output_path}")
        
        # Validate servers
        print("\n🔍 Validating server paths...")
        if not generator.validate_servers():
            print("⚠️  Some server paths may be invalid")
        
        # Install if requested
        if args.install:
            print(f"\n📦 Installing to Claude Desktop ({platform.system()})...")
            if generator.install_config(backup=not args.no_backup):
                print("✅ Installation complete!")
                print("\n📋 Next steps:")
                print("1. Restart Claude Desktop application")
                print("2. Check that MCP servers appear in Claude Desktop")
            else:
                print("❌ Installation failed")
                return 1
        else:
            print(f"\n💡 To install to Claude Desktop, run:")
            print(f"   python {Path(__file__).name} --install")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())