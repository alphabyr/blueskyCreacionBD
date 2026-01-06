"""
Módulo para extraer características de perfiles y posts de Bluesky
"""
import numpy as np
import re
from datetime import datetime
from collections import Counter

class FeatureExtractor:
    """Extrae características de un perfil y sus posts para detección de bots"""
    
    def __init__(self):
        pass
    
    def extract_profile_features(self, profile_data, posts_data=None):
        """
        Extrae características de un perfil de Bluesky
        
        Args:
            profile_data: Dict con datos del perfil
            posts_data: List de posts (opcional)
            
        Returns:
            Dict con características calculadas
        """
        features = {}
        
        # ── CARACTERÍSTICAS DE PERFIL ──
        
        # Edad de la cuenta (días desde creación)
        if 'created_at' in profile_data and profile_data['created_at']:
            created = self._parse_date(profile_data['created_at'])
            if created:
                # Usar datetime con timezone UTC
                from datetime import timezone
                now_utc = datetime.now(timezone.utc)
                # Si created no tiene timezone, asumirlo como UTC
                if created.tzinfo is None:
                    from datetime import timezone
                    created = created.replace(tzinfo=timezone.utc)
                features['account_age_days'] = (now_utc - created).days
            else:
                features['account_age_days'] = 0
        else:
            features['account_age_days'] = 0
        
        # Contadores básicos
        features['followers_count'] = profile_data.get('followers_count', 0) or 0
        features['following_count'] = profile_data.get('follows_count', 0) or 0
        features['posts_count'] = profile_data.get('posts_count', 0) or 0
        
        # Ratio de seguidores
        if features['following_count'] > 0:
            features['followers_ratio'] = features['followers_count'] / features['following_count']
        else:
            features['followers_ratio'] = features['followers_count']
        
        # Información del perfil
        features['has_avatar'] = 1 if profile_data.get('avatar') else 0
        features['bio_length'] = len(profile_data.get('description', '') or '')
        features['display_name_length'] = len(profile_data.get('display_name', '') or '')
        
        # Análisis del handle
        handle = profile_data.get('handle', '')
        features['handle_has_many_numbers'] = self._has_many_numbers(handle)
        
        # Posts por día
        if features['account_age_days'] > 0:
            features['posts_per_day'] = features['posts_count'] / features['account_age_days']
        else:
            features['posts_per_day'] = 0
        
        # ── CARACTERÍSTICAS DE POSTS ──
        if posts_data and len(posts_data) > 0:
            post_features = self._extract_post_features(posts_data)
            features.update(post_features)
        else:
            # Características por defecto si no hay posts
            features.update({
                'avg_post_length': 0,
                'std_post_length': 0,
                'post_interval_std': 0,
                'night_posts_ratio': 0,
                'repost_ratio': 0,
                'url_ratio': 0,
                'avg_engagement': 0,
                'vocabulary_diversity': 0,
                'post_similarity_avg': 0
            })
        
        return features
    
    def _extract_post_features(self, posts):
        """Extrae características de una lista de posts"""
        features = {}
        
        if not posts or len(posts) == 0:
            return {
                'avg_post_length': 0,
                'std_post_length': 0,
                'post_interval_std': 0,
                'night_posts_ratio': 0,
                'repost_ratio': 0,
                'url_ratio': 0,
                'avg_engagement': 0,
                'vocabulary_diversity': 0,
                'post_similarity_avg': 0
            }
        
        # Longitud de posts
        post_lengths = [len(post.get('text', '')) for post in posts]
        features['avg_post_length'] = np.mean(post_lengths) if post_lengths else 0
        features['std_post_length'] = np.std(post_lengths) if len(post_lengths) > 1 else 0
        
        # Intervalos entre posts
        timestamps = []
        for post in posts:
            if 'createdAt' in post:
                ts = self._parse_date(post['createdAt'])
                if ts:
                    timestamps.append(ts)
        
        if len(timestamps) > 1:
            timestamps.sort()
            intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() / 60  # en minutos
                        for i in range(len(timestamps)-1)]
            features['post_interval_std'] = np.std(intervals) if intervals else 0
        else:
            features['post_interval_std'] = 0
        
        # Posts nocturnos (00:00 - 06:00)
        night_posts = sum(1 for ts in timestamps if ts.hour >= 0 and ts.hour < 6)
        features['night_posts_ratio'] = night_posts / len(posts) if posts else 0
        
        # Ratio de reposts (posts sin texto original o muy cortos)
        reposts = sum(1 for post in posts if len(post.get('text', '')) < 10)
        features['repost_ratio'] = reposts / len(posts) if posts else 0
        
        # Ratio de posts con URLs
        url_posts = sum(1 for post in posts if 'http' in post.get('text', '').lower())
        features['url_ratio'] = url_posts / len(posts) if posts else 0
        
        # Engagement promedio
        engagements = [
            (post.get('likeCount', 0) or 0) + (post.get('replyCount', 0) or 0)
            for post in posts
        ]
        features['avg_engagement'] = np.mean(engagements) if engagements else 0
        
        # Diversidad de vocabulario
        all_words = []
        for post in posts:
            text = post.get('text', '').lower()
            words = re.findall(r'\b\w+\b', text)
            all_words.extend(words)
        
        if all_words:
            unique_words = len(set(all_words))
            total_words = len(all_words)
            features['vocabulary_diversity'] = unique_words / total_words if total_words > 0 else 0
        else:
            features['vocabulary_diversity'] = 0
        
        # Similitud promedio entre posts (basado en palabras compartidas)
        post_texts = [post.get('text', '') for post in posts]
        features['post_similarity_avg'] = self._calculate_avg_similarity(post_texts)
        
        return features
    
    def _has_many_numbers(self, handle):
        """Detecta si el handle tiene muchos números (>= 5 dígitos consecutivos)"""
        if not handle:
            return 0
        # Buscar secuencias de 5+ dígitos
        if re.search(r'\d{5,}', handle):
            return 1
        return 0
    
    def _parse_date(self, date_str):
        """Parsea una fecha de Bluesky a datetime"""
        if not date_str:
            return None
        try:
            # Formato ISO 8601
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return None
    
    def _calculate_avg_similarity(self, texts):
        """Calcula similitud promedio entre textos (Jaccard simplificado)"""
        if len(texts) < 2:
            return 0
        
        similarities = []
        for i in range(len(texts)):
            for j in range(i+1, len(texts)):
                words1 = set(texts[i].lower().split())
                words2 = set(texts[j].lower().split())
                
                if len(words1 | words2) > 0:
                    sim = len(words1 & words2) / len(words1 | words2)
                    similarities.append(sim)
        
        return np.mean(similarities) if similarities else 0
