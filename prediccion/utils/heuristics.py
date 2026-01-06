"""
Módulo para aplicar reglas heurísticas de clasificación
"""

class HeuristicLabeler:
    """Aplica reglas heurísticas para etiquetar perfiles como bot o humano"""
    
    def __init__(self, config):
        """
        Args:
            config: Dict con configuración de heurísticas
        """
        # Umbrales ULTRA-BAJOS para clasificar más del 95% de perfiles
        self.min_score_bot = config.get('min_score_bot', 0.5)
        self.min_score_humano = config.get('min_score_humano', 0.8)
    
    def label_profile(self, features):
        """
        Etiqueta un perfil usando sistema de scoring ponderado con umbrales asimétricos
        
        Args:
            features: Dict con características del perfil
            
        Returns:
            int: 1 (bot), 0 (humano), o -1 (incierto)
        """
        # Calcular score neto (positivo = humano, negativo = bot)
        net_score = self._calculate_weighted_score(features)
        
        # UMBRALES ULTRA-AGRESIVOS: clasificar más del 95% de perfiles
        if net_score <= -self.min_score_bot:
            return 1  # Bot (umbral -0.5 = ULTRA AGRESIVO)
        elif net_score >= self.min_score_humano:
            return 0  # Humano (umbral +0.8 = ULTRA AGRESIVO)
        else:
            return -1  # Incierto SOLO si -0.5 < score < +0.8 (rango MÍNIMO)
    
    def _calculate_weighted_score(self, f):
        """
        Calcula score neto ponderado
        Positivo = indicadores de humano
        Negativo = indicadores de bot
        
        Returns:
            float: Score neto (-10 a +10)
        """
        score = 0.0
        
        # ═══════════════════════════════════════════════════════════
        # INDICADORES DE BOT (restan puntos) - AJUSTADOS PARA MAYOR SENSIBILIDAD
        # ═══════════════════════════════════════════════════════════
        
        # 🤖 Perfil sin personalizar (MUY fuerte indicador de bot)
        if f.get('has_avatar', 0) == 0 and f.get('bio_length', 0) < 10:
            score -= 4  # Incrementado de 3
        elif f.get('has_avatar', 0) == 0:
            score -= 2  # Incrementado de 1.5
        elif f.get('bio_length', 0) < 20:  # Umbral más alto (antes < 10)
            score -= 1.5  # Incrementado de 1
        
        # 🤖 Handle sospechoso con muchos números
        if f.get('handle_has_many_numbers', 0) == 1:
            score -= 2.5  # Incrementado de 2
        
        # 🤖 Actividad extremadamente alta
        posts_per_day = f.get('posts_per_day', 0)
        if posts_per_day > 100:
            score -= 3.5  # Incrementado de 3
        elif posts_per_day > 50:
            score -= 2.5  # Incrementado de 2
        elif posts_per_day > 20:  # Umbral reducido (antes 30)
            score -= 1.5  # Incrementado de 1
        
        # 🤖 Cuenta nueva MUY activa (señal de spam)
        account_age = f.get('account_age_days', 0)
        if account_age < 30 and f.get('posts_count', 0) > 300:  # Umbral reducido (antes 500)
            score -= 3.5  # Incrementado de 3
        elif account_age < 90 and f.get('posts_count', 0) > 800:  # Umbral ajustado
            score -= 2.5  # Incrementado de 2
        
        # 🤖 Ratio de followers extremadamente bajo
        followers_ratio = f.get('followers_ratio', 0)
        if followers_ratio < 0.01 and f.get('following_count', 0) > 500:
            score -= 3  # Incrementado de 2.5
        elif followers_ratio < 0.05 and f.get('following_count', 0) > 200:
            score -= 2  # Incrementado de 1.5
        elif followers_ratio < 0.1 and f.get('following_count', 0) > 100:  # Nueva regla
            score -= 1
        
        # 🤖 Alta ratio de reposts (cuenta retweeteadora)
        repost_ratio = f.get('repost_ratio', 0)
        if repost_ratio > 0.8:
            score -= 2
        elif repost_ratio > 0.6:
            score -= 1
        
        # 🤖 Posts nocturnos muy altos (bot 24/7)
        night_ratio = f.get('night_posts_ratio', 0)
        if night_ratio > 0.4:
            score -= 1.5
        
        # 🤖 Intervalos de posts muy regulares (automatizado)
        post_interval_std = f.get('post_interval_std', float('inf'))
        if 0 < post_interval_std < 5:
            score -= 2
        
        # ═══════════════════════════════════════════════════════════
        # INDICADORES DE HUMANO (suman puntos)
        # ═══════════════════════════════════════════════════════════
        
        # 👤 Perfil completo y personalizado (fuerte indicador humano)
        if f.get('has_avatar', 0) == 1 and f.get('bio_length', 0) > 100:
            score += 3
        elif f.get('has_avatar', 0) == 1 and f.get('bio_length', 0) > 50:
            score += 2
        elif f.get('has_avatar', 0) == 1:
            score += 1
        
        # 👤 Cuenta antigua (señal de confianza)
        if account_age > 730:  # > 2 años
            score += 2.5
        elif account_age > 365:  # > 1 año
            score += 1.5
        elif account_age > 180:  # > 6 meses
            score += 0.5
        
        # 👤 Buen engagement (followers)
        followers_count = f.get('followers_count', 0)
        if followers_count > 1000:
            score += 2.5
        elif followers_count > 500:
            score += 2
        elif followers_count > 100:
            score += 1.5
        elif followers_count > 50:
            score += 1
        
        # 👤 Ratio de followers saludable
        if followers_ratio > 0.5:
            score += 2
        elif followers_ratio > 0.2:
            score += 1.5
        elif followers_ratio > 0.1:
            score += 1
        
        # 👤 Actividad moderada (humana)
        if 0.5 < posts_per_day < 15:
            score += 2
        elif 0.1 < posts_per_day < 30:
            score += 1
        
        # 👤 Diversidad de vocabulario (contenido original)
        vocab_diversity = f.get('vocabulary_diversity', 0)
        if vocab_diversity > 0.6:
            score += 2
        elif vocab_diversity > 0.4:
            score += 1
        
        # 👤 Posts variados (no spam)
        post_similarity = f.get('post_similarity_avg', 1)
        if post_similarity < 0.2:
            score += 1.5
        elif post_similarity < 0.4:
            score += 0.5
        
        # 👤 Buen engagement promedio
        avg_engagement = f.get('avg_engagement', 0)
        if avg_engagement > 10:
            score += 2
        elif avg_engagement > 5:
            score += 1
        elif avg_engagement > 2:
            score += 0.5
        
        return score
