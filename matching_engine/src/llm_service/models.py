from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class MatchItem(BaseModel):
    """
    具体的技能、门槛或职业素养匹配项
    """
    name: str = Field(..., description="匹配项名称，必须与岗位画像中的字段完全一致")
    status: Literal["具备", "缺失"] = Field(..., description="是否具备该项能力")
    evidence: str = Field(..., description="判定为具备的原文证据，或判定为缺失的说明（如：简历中未体现相关经历或技能）")

class SummaryMatch(BaseModel):
    """
    宏观匹配度总结
    """
    matching_degree: Literal["高", "中", "低"] = Field(..., description="整体匹配程度")
    summary: str = Field(..., description="对学生与岗位匹配度的宏观评价（约100字）")

class MatchingResult(BaseModel):
    """
    匹配引擎的最终结构化输出
    """
    skills: List[MatchItem] = Field(..., description="技能匹配集合")
    thresholds: List[MatchItem] = Field(..., description="基础门槛匹配集合")
    professionalism: List[MatchItem] = Field(..., description="职业素养匹配集合")
    summary: SummaryMatch = Field(..., description="匹配度综述")
