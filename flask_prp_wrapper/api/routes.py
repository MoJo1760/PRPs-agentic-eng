"""Main API routes for Flask PRP Wrapper."""

import asyncio
import logging
from datetime import datetime
from typing import Dict
from flask import request, jsonify
import traceback

from . import bp
from ..models.business_concept import BusinessConceptRequest, BusinessConceptResponse
from ..models.questionnaire import (
    QuestionnaireGenerationRequest,
    QuestionnaireResponse,
    QuestionnaireSession,
)
from ..services.questioning_engine import QuestioningEngine
from ..services.research_service import ResearchService
from ..services.prp_generator import PRPGenerator
from ..services.iterative_research_engine import IterativeResearchEngine
from ..services.gap_analysis_service import GapAnalysisService
from ..services.coverage_validator import CoverageValidator
from ..models.coverage_metrics import StoppingCriteria

logger = logging.getLogger(__name__)

# Initialize services (would typically be done via dependency injection)
questioning_engine = QuestioningEngine()
research_service = ResearchService()
prp_generator = PRPGenerator()
iterative_research_engine = IterativeResearchEngine()
gap_analysis_service = GapAnalysisService()
coverage_validator = CoverageValidator()

# In-memory storage for demo (would use Redis/database in production)
sessions_store: Dict[str, Dict] = {}
concepts_store: Dict[str, Dict] = {}


@bp.route("/concepts", methods=["POST"])
def submit_business_concept():
    """Submit a business concept and initiate analysis."""
    try:
        # Validate request data
        try:
            concept_data = BusinessConceptRequest(**request.json)
        except Exception as e:
            return jsonify({"error": "Invalid request data", "details": str(e)}), 400

        # Generate concept analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            analysis = loop.run_until_complete(
                questioning_engine.analyze_business_concept(concept_data)
            )
        finally:
            loop.close()

        # Store concept and analysis
        concept_id = analysis.concept_id
        concepts_store[concept_id] = {
            "concept": concept_data.dict(),
            "analysis": analysis.dict(),
            "created_at": datetime.utcnow().isoformat(),
            "status": "analyzing",
        }

        # Generate response
        response = BusinessConceptResponse(
            concept_id=concept_id,
            title=concept_data.title,
            description=concept_data.description,
            domain=concept_data.domain,
            business_model=concept_data.business_model,
            created_at=analysis.analysis_timestamp,
            status="ready_for_questions",
            next_step="Generate and answer questionnaire to proceed with PRP creation",
            estimated_questions=min(10, max(5, int(analysis.complexity_score))),
        )

        logger.info(f"Business concept submitted: {concept_id}")
        return jsonify(response.dict()), 201

    except Exception as e:
        logger.error(f"Error submitting business concept: {e}")
        logger.error(traceback.format_exc())
        return jsonify(
            {"error": "Failed to process business concept", "message": str(e)}
        ), 500


@bp.route("/concepts/<concept_id>", methods=["GET"])
def get_business_concept(concept_id: str):
    """Get business concept details and analysis."""
    try:
        if concept_id not in concepts_store:
            return jsonify({"error": "Concept not found"}), 404

        concept_data = concepts_store[concept_id]
        return jsonify(concept_data), 200

    except Exception as e:
        logger.error(f"Error retrieving concept {concept_id}: {e}")
        return jsonify({"error": "Failed to retrieve concept", "message": str(e)}), 500


@bp.route("/concepts/<concept_id>/questions", methods=["POST"])
def generate_questions(concept_id: str):
    """Generate questionnaire for a business concept."""
    try:
        if concept_id not in concepts_store:
            return jsonify({"error": "Concept not found"}), 404

        # Parse request
        request_data = request.json or {}
        questionnaire_request = QuestionnaireGenerationRequest(
            concept_id=concept_id,
            max_questions=request_data.get("max_questions", 10),
            focus_areas=request_data.get("focus_areas"),
            difficulty_level=request_data.get("difficulty_level", "intermediate"),
        )

        # Get concept
        concept_dict = concepts_store[concept_id]["concept"]
        concept = BusinessConceptRequest(**concept_dict)

        # Generate questions
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            questions = loop.run_until_complete(
                questioning_engine.generate_questions(questionnaire_request, concept)
            )
        finally:
            loop.close()

        # Create questionnaire session
        questionnaire_session = questioning_engine.create_questionnaire_session(
            concept_id, questions
        )

        # Store session
        sessions_store[questionnaire_session.session_id] = questionnaire_session.dict()

        # Get first question
        first_question = questioning_engine.get_next_question(questionnaire_session)

        response = {
            "session_id": questionnaire_session.session_id,
            "concept_id": concept_id,
            "total_questions": len(questions),
            "current_question": first_question.dict() if first_question else None,
            "progress": {"completed": 0, "total": len(questions), "percentage": 0.0},
        }

        logger.info(f"Generated {len(questions)} questions for concept {concept_id}")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error generating questions for {concept_id}: {e}")
        logger.error(traceback.format_exc())
        return jsonify(
            {"error": "Failed to generate questions", "message": str(e)}
        ), 500


@bp.route("/questionnaire/<session_id>/answer", methods=["POST"])
def submit_answer(session_id: str):
    """Submit answer to questionnaire question."""
    try:
        if session_id not in sessions_store:
            return jsonify({"error": "Session not found"}), 404

        # Parse response
        try:
            response_data = QuestionnaireResponse(**request.json)
        except Exception as e:
            return jsonify({"error": "Invalid response data", "details": str(e)}), 400

        # Get session
        session_dict = sessions_store[session_id]
        questionnaire_session = QuestionnaireSession(**session_dict)

        # Add response
        success = questioning_engine.add_response(questionnaire_session, response_data)

        if not success:
            return jsonify({"error": "Failed to add response"}), 400

        # Update session in store
        sessions_store[session_id] = questionnaire_session.dict()

        # Get next question
        next_question = questioning_engine.get_next_question(questionnaire_session)
        is_complete = questioning_engine.is_questionnaire_complete(
            questionnaire_session
        )

        response = {
            "session_id": session_id,
            "answer_recorded": True,
            "next_question": next_question.dict() if next_question else None,
            "is_complete": is_complete,
            "progress": {
                "completed": len(questionnaire_session.responses),
                "total": len(questionnaire_session.questions),
                "percentage": questionnaire_session.completion_percentage,
            },
        }

        if is_complete:
            response["message"] = "Questionnaire completed! Ready to generate PRP."
            response["next_step"] = (
                f"/api/v1/concepts/{questionnaire_session.concept_id}/generate-prp"
            )

        logger.info(
            f"Answer submitted for session {session_id}, completion: {questionnaire_session.completion_percentage:.1f}%"
        )
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error submitting answer for session {session_id}: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Failed to submit answer", "message": str(e)}), 500


@bp.route("/questionnaire/<session_id>", methods=["GET"])
def get_questionnaire_session(session_id: str):
    """Get questionnaire session details."""
    try:
        if session_id not in sessions_store:
            return jsonify({"error": "Session not found"}), 404

        session_dict = sessions_store[session_id]
        questionnaire_session = QuestionnaireSession(**session_dict)

        # Get summary
        summary = questioning_engine.get_questionnaire_summary(questionnaire_session)

        response = {
            "session_id": session_id,
            "concept_id": questionnaire_session.concept_id,
            "questions": [q.dict() for q in questionnaire_session.questions],
            "responses": [r.dict() for r in questionnaire_session.responses],
            "summary": summary,
            "is_complete": questionnaire_session.is_complete,
            "completion_percentage": questionnaire_session.completion_percentage,
            "started_at": questionnaire_session.started_at.isoformat(),
            "last_activity": questionnaire_session.last_activity.isoformat(),
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error retrieving session {session_id}: {e}")
        return jsonify({"error": "Failed to retrieve session", "message": str(e)}), 500


@bp.route("/concepts/<concept_id>/generate-prp", methods=["POST"])
def generate_prp(concept_id: str):
    """Generate PRP for a business concept with completed questionnaire."""
    try:
        if concept_id not in concepts_store:
            return jsonify({"error": "Concept not found"}), 404

        # Find completed questionnaire session for this concept
        completed_session = None
        for session_id, session_data in sessions_store.items():
            session = QuestionnaireSession(**session_data)
            if session.concept_id == concept_id and session.is_complete:
                completed_session = session
                break

        if not completed_session:
            return jsonify(
                {
                    "error": "No completed questionnaire found",
                    "message": "Please complete the questionnaire before generating PRP",
                }
            ), 400

        # Get concept
        concept_dict = concepts_store[concept_id]["concept"]
        concept = BusinessConceptRequest(**concept_dict)

        # Conduct research
        logger.info(f"Conducting research for concept {concept_id}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            research_context = loop.run_until_complete(
                research_service.gather_business_domain_context(
                    domain=concept.domain.value if concept.domain else "general",
                    business_model=concept.business_model.value
                    if concept.business_model
                    else "general",
                    concept_description=concept.description,
                )
            )
        finally:
            loop.close()

        # Generate PRP
        logger.info(f"Generating PRP for concept {concept_id}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            generated_prp = loop.run_until_complete(
                prp_generator.generate_prp(
                    concept=concept,
                    questionnaire_session=completed_session,
                    research_context=research_context,
                )
            )
        finally:
            loop.close()

        # Store generated PRP
        prp_data = {
            "prp": generated_prp.__dict__,
            "research_context": research_context.__dict__,
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Update concept status
        concepts_store[concept_id]["prp"] = prp_data
        concepts_store[concept_id]["status"] = "completed"

        response = {
            "concept_id": concept_id,
            "prp_id": generated_prp.id,
            "title": generated_prp.title,
            "quality_metrics": generated_prp.quality_metrics,
            "estimated_complexity": generated_prp.estimated_complexity,
            "validation_commands_count": len(generated_prp.validation_commands),
            "content_length": len(generated_prp.content),
            "template_used": generated_prp.template_used,
            "research_quality_score": research_context.research_quality_score,
            "generated_at": generated_prp.generation_timestamp.isoformat(),
            "download_url": f"/api/v1/prps/{generated_prp.id}/download",
            "preview_url": f"/api/v1/prps/{generated_prp.id}",
        }

        logger.info(
            f"PRP generated successfully: {generated_prp.id} (Quality: {generated_prp.quality_metrics['overall_score']:.1f})"
        )
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error generating PRP for {concept_id}: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Failed to generate PRP", "message": str(e)}), 500


@bp.route("/prps/<prp_id>", methods=["GET"])
def get_prp(prp_id: str):
    """Get PRP details."""
    try:
        # Find PRP in concepts store
        prp_data = None
        concept_id = None

        for cid, concept_data in concepts_store.items():
            if "prp" in concept_data and concept_data["prp"]["prp"]["id"] == prp_id:
                prp_data = concept_data["prp"]
                concept_id = cid
                break

        if not prp_data:
            return jsonify({"error": "PRP not found"}), 404

        generated_prp = prp_data["prp"]
        research_context = prp_data["research_context"]

        response = {
            "prp_id": prp_id,
            "concept_id": concept_id,
            "title": generated_prp["title"],
            "content_preview": generated_prp["content"][:500] + "..."
            if len(generated_prp["content"]) > 500
            else generated_prp["content"],
            "quality_metrics": generated_prp["quality_metrics"],
            "estimated_complexity": generated_prp["estimated_complexity"],
            "validation_commands": generated_prp["validation_commands"],
            "template_used": generated_prp["template_used"],
            "research_summary": {
                "quality_score": research_context["research_quality_score"],
                "official_docs_count": len(
                    research_context["official_documentation_links"]
                ),
                "technical_patterns_count": len(research_context["technical_patterns"]),
                "best_practices_count": len(research_context["best_practices"]),
            },
            "generated_at": generated_prp["generation_timestamp"],
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error retrieving PRP {prp_id}: {e}")
        return jsonify({"error": "Failed to retrieve PRP", "message": str(e)}), 500


@bp.route("/prps/<prp_id>/download", methods=["GET"])
def download_prp(prp_id: str):
    """Download PRP as markdown file."""
    try:
        # Find PRP in concepts store
        prp_data = None

        for concept_data in concepts_store.values():
            if "prp" in concept_data and concept_data["prp"]["prp"]["id"] == prp_id:
                prp_data = concept_data["prp"]
                break

        if not prp_data:
            return jsonify({"error": "PRP not found"}), 404

        generated_prp = prp_data["prp"]

        from flask import Response

        return Response(
            generated_prp["content"],
            mimetype="text/markdown",
            headers={
                "Content-Disposition": f'attachment; filename="{prp_id}.md"',
                "Content-Type": "text/markdown; charset=utf-8",
            },
        )

    except Exception as e:
        logger.error(f"Error downloading PRP {prp_id}: {e}")
        return jsonify({"error": "Failed to download PRP", "message": str(e)}), 500


@bp.route("/status", methods=["GET"])
def get_system_status():
    """Get system status and statistics."""
    try:
        stats = {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": {
                "total_concepts": len(concepts_store),
                "active_sessions": len(sessions_store),
                "completed_prps": len(
                    [c for c in concepts_store.values() if "prp" in c]
                ),
                "average_quality_score": 0.0,
            },
            "services": {
                "questioning_engine": "operational",
                "research_service": "operational",
                "prp_generator": "operational",
            },
        }

        # Calculate average quality score
        quality_scores = []
        for concept_data in concepts_store.values():
            if "prp" in concept_data:
                quality_scores.append(
                    concept_data["prp"]["prp"]["quality_metrics"]["overall_score"]
                )

        if quality_scores:
            stats["statistics"]["average_quality_score"] = sum(quality_scores) / len(
                quality_scores
            )

        return jsonify(stats), 200

    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({"error": "Failed to get system status", "message": str(e)}), 500


@bp.route("/concepts/<concept_id>/iterative-research", methods=["POST"])
def start_iterative_research(concept_id: str):
    """Start iterative research for a business concept."""
    try:
        if concept_id not in concepts_store:
            return jsonify({"error": "Concept not found"}), 404

        # Parse optional parameters
        request_data = request.json or {}
        stopping_criteria = None
        
        if "stopping_criteria" in request_data:
            criteria_data = request_data["stopping_criteria"]
            stopping_criteria = StoppingCriteria(
                min_overall_coverage=criteria_data.get("min_overall_coverage", 95.0),
                min_domain_coverage=criteria_data.get("min_domain_coverage", 85.0),
                min_research_quality_score=criteria_data.get("min_research_quality_score", 7.0),
                max_iterations=criteria_data.get("max_iterations", 5),
                max_research_time_minutes=criteria_data.get("max_research_time_minutes", 30),
            )

        # Get concept
        concept_dict = concepts_store[concept_id]["concept"]
        concept = BusinessConceptRequest(**concept_dict)

        # Get existing research if available
        existing_research = None
        if "prp" in concepts_store[concept_id] and "research_context" in concepts_store[concept_id]["prp"]:
            research_data = concepts_store[concept_id]["prp"]["research_context"]
            from ..services.research_service import ResearchContext
            existing_research = ResearchContext(**research_data)

        # Get questionnaire responses if available
        questionnaire_responses = []
        concept_sessions = [
            s for s in sessions_store.values() 
            if s.get("concept_id") == concept_id and s.get("is_complete", False)
        ]
        if concept_sessions:
            latest_session = concept_sessions[-1]  # Get most recent completed session
            questionnaire_responses = latest_session.get("responses", [])

        # Start iterative research
        logger.info(f"Starting iterative research for concept {concept_id}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            research_result = loop.run_until_complete(
                iterative_research_engine.conduct_iterative_research(
                    concept=concept,
                    existing_research=existing_research,
                    stopping_criteria=stopping_criteria,
                    questionnaire_responses=questionnaire_responses,
                )
            )
        finally:
            loop.close()

        # Store research result
        research_data = {
            "iterative_research": research_result.dict(),
            "started_at": datetime.utcnow().isoformat(),
            "status": "completed" if research_result.success else "failed",
        }

        # Update concept store
        if "iterative_research" not in concepts_store[concept_id]:
            concepts_store[concept_id]["iterative_research"] = research_data
        else:
            concepts_store[concept_id]["iterative_research"].update(research_data)

        # Generate response
        response = {
            "concept_id": concept_id,
            "research_id": research_result.concept_id,
            "success": research_result.success,
            "iterations_completed": len(research_result.iterations),
            "final_coverage": research_result.final_coverage_metrics.overall_coverage,
            "gaps_identified": research_result.total_gaps_identified,
            "gaps_filled": research_result.gaps_filled,
            "official_sources_used": research_result.official_sources_used,
            "questions_generated": research_result.questions_generated,
            "research_time_minutes": research_result.total_research_time_minutes,
            "ready_for_prp_generation": research_result.ready_for_prp_generation,
            "early_stop_reason": research_result.early_stop_reason,
            "quality_score": research_result.final_coverage_metrics.research_quality_score,
        }

        logger.info(
            f"Iterative research completed for {concept_id}: {len(research_result.iterations)} iterations, "
            f"{research_result.final_coverage_metrics.overall_coverage:.1f}% coverage"
        )
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in iterative research for {concept_id}: {e}")
        logger.error(traceback.format_exc())
        return jsonify(
            {"error": "Failed to conduct iterative research", "message": str(e)}
        ), 500


@bp.route("/concepts/<concept_id>/gap-analysis", methods=["POST"])
def analyze_concept_gaps(concept_id: str):
    """Analyze knowledge gaps for a business concept."""
    try:
        if concept_id not in concepts_store:
            return jsonify({"error": "Concept not found"}), 404

        # Get concept
        concept_dict = concepts_store[concept_id]["concept"]
        concept = BusinessConceptRequest(**concept_dict)

        # Get existing research if available
        existing_research = None
        if "prp" in concepts_store[concept_id] and "research_context" in concepts_store[concept_id]["prp"]:
            research_data = concepts_store[concept_id]["prp"]["research_context"]
            from ..services.research_service import ResearchContext
            existing_research = ResearchContext(**research_data)

        # Get questionnaire responses if available
        questionnaire_responses = []
        concept_sessions = [
            s for s in sessions_store.values() 
            if s.get("concept_id") == concept_id and s.get("is_complete", False)
        ]
        if concept_sessions:
            latest_session = concept_sessions[-1]
            questionnaire_responses = latest_session.get("responses", [])

        # Analyze gaps
        logger.info(f"Analyzing gaps for concept {concept_id}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            gap_analysis = loop.run_until_complete(
                gap_analysis_service.analyze_concept_gaps(
                    concept=concept,
                    existing_research=existing_research,
                    questionnaire_responses=questionnaire_responses,
                )
            )
        finally:
            loop.close()

        # Store gap analysis
        gap_data = {
            "gap_analysis": gap_analysis.dict(),
            "analyzed_at": datetime.utcnow().isoformat(),
        }

        if "gap_analysis" not in concepts_store[concept_id]:
            concepts_store[concept_id]["gap_analysis"] = gap_data
        else:
            concepts_store[concept_id]["gap_analysis"].update(gap_data)

        # Generate response
        response = {
            "concept_id": concept_id,
            "analysis_id": gap_analysis.concept_id,
            "total_gaps": len(gap_analysis.identified_gaps),
            "critical_gaps": gap_analysis.critical_gaps_count,
            "high_priority_gaps": gap_analysis.high_priority_gaps_count,
            "coverage_percentage": gap_analysis.coverage_percentage,
            "domain_completeness": gap_analysis.domain_completeness,
            "next_research_areas": gap_analysis.next_research_areas,
            "gaps": [
                {
                    "id": gap.id,
                    "category": gap.category,
                    "description": gap.description,
                    "priority": gap.priority,
                    "confidence_score": gap.confidence_score,
                    "filled": gap.filled,
                }
                for gap in gap_analysis.identified_gaps
            ],
        }

        logger.info(
            f"Gap analysis completed for {concept_id}: {len(gap_analysis.identified_gaps)} gaps identified"
        )
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error analyzing gaps for {concept_id}: {e}")
        logger.error(traceback.format_exc())
        return jsonify(
            {"error": "Failed to analyze gaps", "message": str(e)}
        ), 500


@bp.route("/concepts/<concept_id>/gap-targeted-questions", methods=["POST"])
def generate_gap_targeted_questions(concept_id: str):
    """Generate questions specifically targeting identified knowledge gaps."""
    try:
        if concept_id not in concepts_store:
            return jsonify({"error": "Concept not found"}), 404

        # Check if gap analysis exists
        if "gap_analysis" not in concepts_store[concept_id]:
            return jsonify({
                "error": "Gap analysis not found", 
                "message": "Please run gap analysis first"
            }), 400

        # Parse request parameters
        request_data = request.json or {}
        max_questions = request_data.get("max_questions", 10)

        # Get concept and gap analysis
        concept_dict = concepts_store[concept_id]["concept"]
        concept = BusinessConceptRequest(**concept_dict)
        
        gap_analysis_data = concepts_store[concept_id]["gap_analysis"]["gap_analysis"]
        from ..models.gap_analysis import GapAnalysisResult
        gap_analysis = GapAnalysisResult(**gap_analysis_data)

        # Generate gap-targeted questions
        logger.info(f"Generating gap-targeted questions for concept {concept_id}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            targeted_questions = loop.run_until_complete(
                questioning_engine.generate_gap_targeted_questions(
                    gaps=gap_analysis.identified_gaps,
                    concept=concept,
                    max_questions=max_questions,
                )
            )
        finally:
            loop.close()

        # Store the questions
        question_data = {
            "questions": [q.dict() for q in targeted_questions],
            "generated_at": datetime.utcnow().isoformat(),
            "gaps_targeted": len(gap_analysis.identified_gaps),
        }

        if "gap_targeted_questions" not in concepts_store[concept_id]:
            concepts_store[concept_id]["gap_targeted_questions"] = question_data
        else:
            concepts_store[concept_id]["gap_targeted_questions"].update(question_data)

        response = {
            "concept_id": concept_id,
            "questions_generated": len(targeted_questions),
            "gaps_targeted": len(gap_analysis.identified_gaps),
            "questions": [q.dict() for q in targeted_questions],
        }

        logger.info(
            f"Generated {len(targeted_questions)} gap-targeted questions for concept {concept_id}"
        )
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error generating gap-targeted questions for {concept_id}: {e}")
        logger.error(traceback.format_exc())
        return jsonify(
            {"error": "Failed to generate gap-targeted questions", "message": str(e)}
        ), 500


@bp.route("/concepts/<concept_id>/research-progress", methods=["GET"])
def get_research_progress(concept_id: str):
    """Get current research progress for a concept."""
    try:
        if concept_id not in concepts_store:
            return jsonify({"error": "Concept not found"}), 404

        concept_data = concepts_store[concept_id]
        
        # Build progress summary
        progress = {
            "concept_id": concept_id,
            "status": concept_data.get("status", "unknown"),
            "has_gap_analysis": "gap_analysis" in concept_data,
            "has_iterative_research": "iterative_research" in concept_data,
            "has_prp": "prp" in concept_data,
        }

        # Add gap analysis details if available
        if "gap_analysis" in concept_data:
            gap_data = concept_data["gap_analysis"]["gap_analysis"]
            progress["gap_analysis"] = {
                "total_gaps": len(gap_data["identified_gaps"]),
                "critical_gaps": gap_data["critical_gaps_count"],
                "coverage_percentage": gap_data["coverage_percentage"],
                "analyzed_at": concept_data["gap_analysis"]["analyzed_at"],
            }

        # Add iterative research details if available
        if "iterative_research" in concept_data:
            research_data = concept_data["iterative_research"]["iterative_research"]
            progress["iterative_research"] = {
                "success": research_data["success"],
                "iterations_completed": len(research_data["iterations"]),
                "final_coverage": research_data["final_coverage_metrics"]["overall_coverage"],
                "gaps_filled": research_data["gaps_filled"],
                "ready_for_prp": research_data["ready_for_prp_generation"],
                "research_time_minutes": research_data["total_research_time_minutes"],
            }

        # Add questionnaire progress if available
        concept_sessions = [
            s for s in sessions_store.values() 
            if s.get("concept_id") == concept_id
        ]
        if concept_sessions:
            latest_session = concept_sessions[-1]
            progress["questionnaire"] = {
                "session_id": latest_session["session_id"],
                "completion_percentage": latest_session["completion_percentage"],
                "is_complete": latest_session["is_complete"],
                "total_questions": len(latest_session["questions"]),
                "responses_count": len(latest_session["responses"]),
            }

        return jsonify(progress), 200

    except Exception as e:
        logger.error(f"Error getting research progress for {concept_id}: {e}")
        return jsonify(
            {"error": "Failed to get research progress", "message": str(e)}
        ), 500


# Error handlers
@bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify(
        {"error": "Not found", "message": "The requested resource was not found"}
    ), 404


@bp.errorhandler(400)
def bad_request(error):
    """Handle 400 errors."""
    return jsonify({"error": "Bad request", "message": "The request was invalid"}), 400


@bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify(
        {"error": "Internal server error", "message": "An unexpected error occurred"}
    ), 500
