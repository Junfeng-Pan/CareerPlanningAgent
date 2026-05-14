from typing import List, Optional
from pydantic import BaseModel, Field

class ProfileItem(BaseModel):
    """画像条目：技能/门槛/职业素养"""
    name: str = Field(..., description="项目名称")
    evidence: str = Field(..., description="要求摘要/详细说明")

class DevelopmentPath(BaseModel):
    """发展路径"""
    path: str = Field(..., description="发展路径，使用'-'分隔，如：初级工程师 - 中级工程师 - 高级 - 架构师")
    requisitions: str = Field(..., description="走这条发展路径需要的资格与技能")

class JobProfile(BaseModel):
    """
    岗位画像结构化模型

    字段说明：
    - name: 岗位类型名称
    - summary: 岗位综述
    - skills: 专业技能要求
    - thresholds: 基础门槛要求
    - professionalism: 职业素养要求
    - paths: 发展路径（可选，用于职业规划）
    """
    name: str = Field(..., description="岗位类型名称，例如：Java 工程师、C_C++")
    summary: str = Field(..., description="岗位综述：对该岗位职责核心、行业地位及主要工作内容的宏观总结")
    skills: List[ProfileItem] = Field(default_factory=list, description="专业技能要求：该岗位必须掌握的硬技能、工具、框架或行业知识")
    thresholds: List[ProfileItem] = Field(default_factory=list, description="基础门槛要求：入职该岗位的刚性过滤条件（学历、经验、证书等）")
    professionalism: List[ProfileItem] = Field(default_factory=list, description="职业素养要求：软技能、工作态度、价值观及沟通协调能力")
    paths: Optional[List[DevelopmentPath]] = Field(default_factory=list, description="职业发展路径及要求")