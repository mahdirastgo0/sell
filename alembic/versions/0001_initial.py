from alembic import op
import sqlalchemy as sa
revision='0001_initial'; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    op.create_table('users', sa.Column('id',sa.Integer,primary_key=True),sa.Column('telegram_id',sa.BigInteger,unique=True),sa.Column('username',sa.String(255)),sa.Column('first_name',sa.String(255)),sa.Column('created_at',sa.DateTime(timezone=True)),sa.Column('updated_at',sa.DateTime(timezone=True)))
    op.create_index('ix_users_telegram_id','users',['telegram_id'])
    op.create_table('plans', sa.Column('id',sa.Integer,primary_key=True),sa.Column('name',sa.String(100)),sa.Column('description',sa.Text),sa.Column('price',sa.BigInteger),sa.Column('volume_gb',sa.Integer),sa.Column('duration_days',sa.Integer),sa.Column('inbound_id',sa.Integer),sa.Column('enabled',sa.Boolean),sa.Column('sort_order',sa.Integer),sa.Column('created_at',sa.DateTime(timezone=True)),sa.Column('updated_at',sa.DateTime(timezone=True)))
    op.create_table('orders', sa.Column('id',sa.Integer,primary_key=True),sa.Column('user_id',sa.Integer,sa.ForeignKey('users.id')),sa.Column('plan_id',sa.Integer,sa.ForeignKey('plans.id')),sa.Column('status',sa.String(30)),sa.Column('amount',sa.BigInteger),sa.Column('created_at',sa.DateTime(timezone=True)),sa.Column('updated_at',sa.DateTime(timezone=True)))
    op.create_index('ix_orders_user_id','orders',['user_id']); op.create_index('ix_orders_status','orders',['status'])
    op.create_table('payments',sa.Column('id',sa.Integer,primary_key=True),sa.Column('order_id',sa.Integer,sa.ForeignKey('orders.id'),unique=True),sa.Column('receipt_file_id',sa.Text),sa.Column('status',sa.String(30)),sa.Column('reviewed_by',sa.BigInteger),sa.Column('review_note',sa.Text),sa.Column('created_at',sa.DateTime(timezone=True)),sa.Column('reviewed_at',sa.DateTime(timezone=True)))
    op.create_index('ix_payments_status','payments',['status'])
    op.create_table('services',sa.Column('id',sa.Integer,primary_key=True),sa.Column('user_id',sa.Integer,sa.ForeignKey('users.id')),sa.Column('order_id',sa.Integer,sa.ForeignKey('orders.id'),unique=True),sa.Column('plan_id',sa.Integer,sa.ForeignKey('plans.id')),sa.Column('inbound_id',sa.Integer),sa.Column('email',sa.String(255),unique=True),sa.Column('sub_id',sa.String(255),unique=True),sa.Column('uuid',sa.String(100)),sa.Column('enabled',sa.Boolean),sa.Column('created_at',sa.DateTime(timezone=True)))
    op.create_index('ix_services_user_id','services',['user_id'])
    op.create_table('settings',sa.Column('key',sa.String(100),primary_key=True),sa.Column('value',sa.Text))
def downgrade():
    op.drop_table('services');op.drop_table('payments');op.drop_table('orders');op.drop_index('ix_users_telegram_id',table_name='users');op.drop_table('plans');op.drop_table('users');op.drop_table('settings')
