#!/bin/bash

echo "🧹 Cleaning up Agent Fight Club..."
echo "⚠️  This will remove all containers, volumes, and data!"
read -p "Are you sure? (y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker compose down -v
    rm -f backend/combat.db
    rm -f backend/test.db
    echo "✅ Cleanup complete!"
else
    echo "Cancelled."
fi
