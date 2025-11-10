import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.work_order import WorkOrder
from models.work_result import WorkResult
from models.master_operation import MasterOperation
from models.master_equipment import MasterEquipment
from models.master_product import MasterProduct
from models.master_operation_standard import MasterOperationStandard
from datetime import datetime, timedelta


def get_dashboard_data(db: Session):
    
    # 1. 작업지시 데이터 조회
    orders_query = (
        db.query(
            WorkOrder.order_id,
            WorkOrder.product_id,
            WorkOrder.planned_qty,
            WorkOrder.status,
            WorkOrder.created_ts,
            WorkOrder.start_ts,
            WorkOrder.end_ts,
            MasterProduct.name.label("product_name"),
        )
        .join(MasterProduct, WorkOrder.product_id == MasterProduct.product_id)
        .all()
    )
    
    # DataFrame 변환
    df_orders = pd.DataFrame([{
        "order_id": str(r.order_id),
        "product_id": r.product_id,
        "product_name": r.product_name,
        "planned_qty": r.planned_qty,
        "status": r.status,
        "created_ts": r.created_ts,
        "start_ts": r.start_ts,
        "end_ts": r.end_ts,
    } for r in orders_query])
    
    # 2. 작업실적 데이터 조회
    results_query = (
        db.query(
            WorkResult.result_id,
            WorkResult.order_id,
            WorkResult.operation_seq,
            WorkResult.equipment_id,
            WorkResult.start_ts,
            WorkResult.end_ts,
            WorkOrder.product_id,
            WorkOrder.planned_qty,
            MasterOperation.operation_name,
            MasterEquipment.name.label("equipment_name"),
        )
        .join(WorkOrder, WorkResult.order_id == WorkOrder.order_id)
        .join(MasterOperation, WorkResult.operation_seq == MasterOperation.operation_seq)
        .outerjoin(MasterEquipment, WorkResult.equipment_id == MasterEquipment.equipment_id)
        .all()
    )
    
    # DataFrame 변환
    df_results = pd.DataFrame([{
        "result_id": str(r.result_id),
        "order_id": str(r.order_id),
        "operation_seq": r.operation_seq,
        "operation_name": r.operation_name,
        "equipment_id": r.equipment_id,
        "equipment_name": r.equipment_name,
        "start_ts": r.start_ts,
        "end_ts": r.end_ts,
        "product_id": r.product_id,
        "planned_qty": r.planned_qty,
    } for r in results_query])
    
    # 3. 표준시간 데이터 조회
    standards_query = db.query(MasterOperationStandard).all()
    standard_times = {
        (s.product_id, s.operation_seq): s.standard_cycle_time_sec
        for s in standards_query
    }

    # 4. 작업시간 계산
    if not df_results.empty:
        df_results['actual_time_sec'] = (
            pd.to_datetime(df_results['end_ts']) - pd.to_datetime(df_results['start_ts'])
        ).dt.total_seconds()
        df_results['actual_time_min'] = df_results['actual_time_sec'] / 60
        
        # 표준시간 추가
        df_results['standard_time_sec'] = df_results.apply(
            lambda row: standard_times.get((row['product_id'], row['operation_seq']), 0),
            axis=1
        )
        
        # 단위당 실제시간 및 편차율 계산
        df_results['actual_time_per_unit'] = df_results['actual_time_sec'] / df_results['planned_qty']
        df_results['deviation_rate'] = (
            (df_results['actual_time_per_unit'] - df_results['standard_time_sec']) 
            / df_results['standard_time_sec'] * 100
        )
    
    # 5. 제품별 생산 현황
    product_summary = df_orders.groupby(['product_id', 'product_name']).agg({
        'order_id': 'count',
        'planned_qty': 'sum',
    }).reset_index()
    product_summary.columns = ['product_id', 'product_name', 'order_count', 'total_qty']
    product_summary = product_summary.sort_values('order_count', ascending=False)
    
    # Chart.js 데이터 형식
    product_chart = {
        "labels": product_summary['product_name'].tolist(),
        "data": product_summary['order_count'].tolist(),
    }

    # 6. 상태별 작업지시 분포
    status_names = {
        "S0_PLANNED": "계획",
        "S1_READY": "부품준비",
        "S2_ASSEMBLY": "조립",
        "S3_INSPECTION": "검사",
        "S4_PACK": "포장",
        "S5_DONE": "완료",
    }
    #status를 일반 컬럼으로 변경하고 index를 0부터 재할당
    status_summary = df_orders['status'].value_counts().reset_index() 
    status_summary.columns = ['status', 'count']
    status_summary['status_name'] = status_summary['status'].map(status_names)
    
    status_chart = {
        "labels": status_summary['status_name'].tolist(),
        "data": status_summary['count'].tolist(),
    }

    # 7. 공정별 평균 작업시간
    if not df_results.empty:
        operation_summary = df_results.groupby('operation_name')['actual_time_min'].mean().reset_index()
        operation_summary.columns = ['operation_name', 'avg_time_min']
        operation_summary = operation_summary.sort_values('avg_time_min', ascending=False)
        
        operation_chart = {
            "labels": operation_summary['operation_name'].tolist(),
            "data": operation_summary['avg_time_min'].round(2).tolist(),
        }
    else:
        operation_chart = {"labels": [], "data": []}

    # 8. 설비별 작업 건수 (Top 10)
    if not df_results.empty and df_results['equipment_name'].notna().any():
        equipment_summary = df_results['equipment_name'].value_counts().head(10).reset_index()
        equipment_summary.columns = ['equipment_name', 'count']
        
        equipment_chart = {
            "labels": equipment_summary['equipment_name'].tolist(),
            "data": equipment_summary['count'].tolist(),
        }
    else:
        equipment_chart = {"labels": [], "data": []}
    
    # 9. 일별 생산량 추이 (최근 30일)
    completed_orders = df_orders[df_orders['status'] == 'S5_DONE'].copy()
    if not completed_orders.empty:
        completed_orders['completion_date'] = pd.to_datetime(completed_orders['end_ts']).dt.date
        
        # 최근 30일
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        daily_production = completed_orders[
            (completed_orders['completion_date'] >= start_date) &
            (completed_orders['completion_date'] <= end_date)
        ].groupby('completion_date')['planned_qty'].sum().reset_index()
        
        daily_production.columns = ['date', 'qty']
        daily_production = daily_production.sort_values('date')
        
        daily_chart = {
            "labels": [d.strftime('%m/%d') for d in daily_production['date'].tolist()],
            "data": daily_production['qty'].tolist(),
        }
    else:
        daily_chart = {"labels": [], "data": []}
    
    # 10. 편차율 분포 (히스토그램)
    if not df_results.empty and 'deviation_rate' in df_results.columns:
        # -50% ~ 50% 범위를 10개 구간으로
        bins = [-50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50]
        df_results['deviation_bin'] = pd.cut(df_results['deviation_rate'], bins=bins)
        deviation_hist = df_results['deviation_bin'].value_counts().sort_index()
        
        deviation_chart = {
            "labels": [str(interval) for interval in deviation_hist.index],
            "data": deviation_hist.values.tolist(),
        }
    else:
        deviation_chart = {"labels": [], "data": []}
    
    # 11. KPI 요약 지표
    total_orders = len(df_orders)
    completed_orders_count = len(df_orders[df_orders['status'] == 'S5_DONE'])
    in_progress_count = len(df_orders[df_orders['status'].isin(['S1_READY', 'S2_ASSEMBLY', 'S3_INSPECTION', 'S4_PACK'])])
    planned_count = len(df_orders[df_orders['status'] == 'S0_PLANNED'])
    
    completion_rate = (completed_orders_count / total_orders * 100) if total_orders > 0 else 0
    
    avg_deviation = df_results['deviation_rate'].mean() if not df_results.empty and 'deviation_rate' in df_results.columns else 0
    
    kpi = {
        "total_orders": total_orders,
        "completed_orders": completed_orders_count,
        "in_progress": in_progress_count,
        "planned": planned_count,
        "completion_rate": round(completion_rate, 1),
        "avg_deviation_rate": round(avg_deviation, 2),
    }
    
    # 반환 데이터
    return {
        "kpi": kpi,
        "product_chart": product_chart,
        "status_chart": status_chart,
        "operation_chart": operation_chart,
        "equipment_chart": equipment_chart,
        "daily_chart": daily_chart,
        "deviation_chart": deviation_chart,
    }
