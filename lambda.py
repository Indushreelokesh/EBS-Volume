import boto3
from datetime import datetime, timezone, timedelta

# Initialize EC2 client
ec2 = boto3.client('ec2')

# Replace with your actual Volume ID
VOLUME_ID = 'vol-08a44bd2cc81315f6'

def lambda_handler(event, context):
    
    print("===== EBS Backup Automation Started =====")
    
    # -------------------------------
    # 1. Create Snapshot
    # -------------------------------
    try:
        description = f"Automated snapshot - {datetime.now(timezone.utc)}"
        
        response = ec2.create_snapshot(
            VolumeId=VOLUME_ID,
            Description=description
        )
        
        snapshot_id = response['SnapshotId']
        print(f"✅ Snapshot Created: {snapshot_id}")
        
    except Exception as e:
        print(f"❌ Error creating snapshot: {str(e)}")
        return
    
    # -------------------------------
    # 2. Define Retention (30 days)
    # -------------------------------
    retention_days = 30
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
    
    print(f"🗓 Deleting snapshots older than: {cutoff_date}")
    
    # -------------------------------
    # 3. Fetch Snapshots
    # -------------------------------
    try:
        snapshots = ec2.describe_snapshots(
            OwnerIds=['self']
        )['Snapshots']
        
    except Exception as e:
        print(f"❌ Error fetching snapshots: {str(e)}")
        return
    
    # -------------------------------
    # 4. Delete Old Snapshots
    # -------------------------------
    deleted_snapshots = []
    
    for snap in snapshots:
        try:
            # Only check snapshots of this volume
            if snap['VolumeId'] == VOLUME_ID:
                
                start_time = snap['StartTime']
                
                if start_time < cutoff_date:
                    ec2.delete_snapshot(SnapshotId=snap['SnapshotId'])
                    deleted_snapshots.append(snap['SnapshotId'])
                    
        except Exception as e:
            print(f"⚠️ Error processing snapshot {snap.get('SnapshotId')}: {str(e)}")
    
    print(f"🗑 Deleted Snapshots: {deleted_snapshots}")
    
    print("===== EBS Backup Automation Completed =====")
    
    # -------------------------------
    # 5. Return Output
    # -------------------------------
    return {
        "statusCode": 200,
        "created_snapshot": snapshot_id,
        "deleted_snapshots": deleted_snapshots
    }
